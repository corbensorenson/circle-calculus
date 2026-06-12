# Phase II And Application Tracks

This note preserves the application and post-`S^15` context from the browser handoffs without turning the repository into a transcript archive. The canonical operating checklist remains `docs/COMPLETION_ROADMAP.md`.

None of this file changes proof status. A claim is proved only when it has a compiled Lean declaration and passes the repository proof checks.

The exact 2026-06-05 compute-applications browser note is archived at `circle_calculus_codex_handoff/source_logs/04_compute_applications_browser_note.md`; this file keeps the actionable project context curated.

## Novelty Position

Circle Math should be honest about what is known and what may be new.

Known background includes modular arithmetic, complex phase, Fourier analysis, spheres, quaternions, Hopf fibrations, octonions, persistent homology, proof assistants, circulant matrices, FFTs, NTTs, spherical harmonics, and geometric deep learning.

The possible novelty is the integrated system:

- circle-first definitions,
- dimension-indexed theorem roadmaps,
- coil and provenance objects,
- proof-carrying glyphs,
- Lean-certified diagrams,
- Python and MLX executable models,
- paper-linked theorem manifests,
- a shared dictionary that prevents vocabulary drift.

The project should not claim that it replaces standard mathematics. The stronger claim is that it can reorganize cyclic, periodic, spherical, and fibered mathematics into a proof-carrying interface.

## Primary Application Bets

These are the application tracks to keep visible as the proof corpus grows:

- Education and visual intuition for modular arithmetic, primes, coils, winding, spheres, quaternions, and Hopf fibers.
- Proof-carrying diagrams and glyphs: diagram to syntax, theorem id, Lean declaration, proof certificate, and paper section.
- Formal math repository architecture: every concept linked across prose, dictionary, manifest, Lean, Python, examples, and diagrams.
- Cyclic and periodic data analysis: coil signatures, closure profiles, prime-lag scans, antinode maps, and fiber/provenance annotations.
- Proof search by shape: orbit pattern, closure type, gcd signature, antinode pattern, fiber twist, boundary profile, and glyph normal form.
- Number provenance spaces: treating construction history, decompositions, factor lattices, orbit decompositions, and proof history as first-class data.
- Machine learning with explicit periodic, rotational, spherical, phase, and fiber structure where the data actually has that structure.
- Robotics and orientation tooling through `S^3`, unit quaternions, spin ambiguity, interpolation, and rotation constraints.
- Signal and harmonic interfaces: circular convolution, Fourier modes, spherical harmonics, and rotation-aware transforms.
- Physics-style explanation layers for phase, gauge-like redundancy, spin, holonomy, fields, boundaries, and defects, with no physics claims marked as proved before formal support exists.

## Dedicated Circle AI Deep Program

AI is an active first-class application phase. The project should explore all plausible Circle AI avenues, but the claims must stay disciplined:

- phase channels and periodic feature routing,
- cyclic memory slots, alias diagnostics, and retrieval fixtures,
- coil/sparse attention and long-context path selection,
- adapter blocks, CoilRA, block-cyclic adapters, and parameter-sharing layouts,
- RoPE, MultiCoil RoPE, winding-aware positional structure, and torus-valued position views,
- looped and recursive transformers with phase-indexed recurrence schedules, loop-exit certificates, and overthinking guardrails,
- recurrent, state-space, and convolutional sequence models with explicit period structure,
- harmonic, Fourier, circulant, and NTT-adjacent features,
- geometry-aware quaternion, spherical, Hopf/fiber, and rotation representations,
- proof-carrying model components where finite indexing, rewrite legality, or schedule behavior can be Lean-checked, and
- MLX/Mac-compatible prototypes with CPU reference parity.

For each avenue, keep four lanes separate:

```text
Lean theorem target -> Python/MLX executable fixture -> benchmark against ordinary baselines -> research hypothesis
```

Positive periodic fixtures must include negative controls where circular structure should not help. Benchmarks should report quality, runtime, memory, parameter count, and interpretability separately. Do not claim AI improvement, attention replacement, better RoPE, parameter efficiency, or speed without a reproducible benchmark script, an ordinary baseline, and a clear metric.

Roadmap-grade AI acceptance criteria:

- Every AI avenue should have a paper section, manifest anchor, dictionary vocabulary, executable fixture, and Living Book explanation before it is treated as a mature project claim.
- Every positive benchmark fixture needs at least one ordinary baseline and at least one negative or mismatch control.
- MLX prototypes must start from CPU-reference parity and report MLX availability honestly.
- Learned-model work should compare against standard dense, RoPE, LoRA, sliding-window, dilated, full-attention, long-convolution, and state-space baselines when those baselines match the question; `AIA-B0004` and `AIA-B0005` are only the first learned-feature and harmonic-feature baseline scaffolds.
- Looped/recursive transformer work starts with `AIM-B0003`, a deterministic recurrence-schedule fixture, `AIM-B0011`, a deterministic loop-exit certificate fixture, `AIM-B0005`, a deterministic token-level recurrence routing fixture, `AIM-B0012`, a deterministic learned token-level recurrence fixture, `AIM-B0006`, a deterministic training-free loop-wrapper fixture, `AIM-B0007`, a deterministic middle-block recurrence fixture, `AIM-B0013`, a deterministic learned middle-block recurrence fixture, `AIM-B0008`, a deterministic multi-resolution recurrence fixture, `AIM-B0014`, a deterministic learned multi-resolution recurrence fixture, and `AIM-B0009`, a deterministic learned recurrence-schedule fixture. Coil/local attention routing now has `AIM-B0010`, a deterministic learned content-gate retrieval fixture. These lanes should expand toward dense transformer depth, Universal Transformer recurrence, fixed looped transformers, adaptive early-exit models, recurrent-memory transformers, token-level Mixture-of-Recursions, sparse/MoE looped models, RWKV/Mamba-style recurrent/state-space models, learned gates, full/sparse attention baselines, and ordinary nonrecursive transformer baselines before any reasoning-depth, retrieval-quality, context-length, or parameter-efficiency claim.
- Geometry-aware AI work should be staged: `S^1` phase first, `S^3` quaternion/orientation next, and `S^7` or octonionic hypotheses only after the lower-dimensional evidence is stable.
- The Living Book AI path should teach the idea before source links: problem, ordinary baseline, circular hypothesis, Lean-proved boundary, Python/MLX fixture, benchmark result, and limitations.

Current Theseus-Hive transfer state: the companion scored private benchmark layer now includes `circle_phase_feature_sequence_ablation_v1`, `circle_mixer_route_ranker_ablation_v1`, `circle_mixer_router_head_attachment_v1`, `circle_seed_rule_exact_regeneration_v1`, `circle_seed_rule_source_change_stress_v1`, `circle_seed_rule_workflow_tool_card_rebuild_v1`, and `circle_seed_rule_update_cycle_effort_v1` alongside the candidate-fanout, semantic-context, full-frontier semantic, recurrence work-budget, and context-memory reports. The phase scorer reads private sequence/category rows and exports only aggregate counts and accuracies: on `9750` rows with an ordered `7800`/`1950` train/eval split, Circle periods `[5, 7]`, relative period `5`, wrong periods `[6, 8]`, and no-phase majority all report accuracy `0.528205`. The mixer scorer reads local Octopus router traces and exports only aggregate route/ranker metrics: on `94` examples, dense hashed, Circle circulant, and Circle block-cyclic transforms all report heldout exact-set accuracy `1.0`; the best Circle policy ties the best ordinary quality score with parameter count `8` versus `2048`. The router-head attachment scorer then compares those same mixer policies with `14` current Octopus holdout decisions: dense hashed, Circle circulant, and Circle block-cyclic all report router-head agreement `1.0`, low-rank reports `0.714286`, no-mixer reports `0.0`, and the best Circle policy again uses `8` counted parameters versus `2048` for the best ordinary dense policy. The actual Octopus trainer now also has an opt-in `--circle-mixer circulant|block_cyclic|circulant_residual|block_cyclic_residual` shadow path plus the aggregate benchmark id `circle_router_head_mixer_shadow_training_v1`; on the current local ORA report, arm registry, and workflow routing traces, baseline, pure circulant, pure block-cyclic, residual circulant, and residual block-cyclic all report `14`/`14` holdout exact-set accuracy, arm micro-F1 `1.0`, risk-routing accuracy `1.0`, exact mismatch count `0`, and zero external inference calls, with `4` shared kernel parameters in each Circle trainer mode. A `5`-repetition timing/memory run recorded stable aggregate metrics; validation-run median elapsed time is `8.926` ms baseline, `105.975` ms pure circulant, `110.399` ms pure block-cyclic, `104.434` ms residual circulant, and `112.164` ms residual block-cyclic, and median Python `tracemalloc` peak bytes are `117078`, `335105`, `338973`, `447449`, and `438130`, so runtime and memory are not win claims. The keyword-boundary contrastive diagnostic adds `45` holdout examples: no-mixer exact accuracy is `1.0`, pure circulant and pure block-cyclic are `0.6667`, and full-gain residual circulant/residual block-cyclic improve to `0.8667`/`0.8222` while still trailing baseline; the quality-only gain sweep finds residual gains `0.05`, `0.1`, `0.25`, and `0.5` preserve baseline exactness on this synthetic diagnostic. The seed-rule exact scorer reads local provenance/tool-memory summaries and exactly regenerates `75` safe envelope records with verifier residual count `0`; its source/rule recipe is `527` bytes versus `13291` bytes for object-only storage. The seed-rule stress scorer applies `4` deterministic source-change scenarios and `20` downstream reuse queries; Circle average description length is `590.0` versus object-only `10344.75`, and Circle average edit cost is `463.75` versus object-only `6327.5`, while exact regeneration and reuse tie object-only at `1.0`. The workflow/tool-card rebuild scorer reads `72` safe workflow/card sources, rebuilds `188` safe envelope records, and records Circle automated rebuild work units `9334` versus object-only `59730` while exact rebuild and reuse tie object-only at `1.0`; human edit time is not measured. The update-cycle effort instrumentor reads `13` safe sources and `289` aggregate event records, finds `212` runtime fields, finds `3` review-step fields totaling `15.0` review steps, and now finds paired `object_only` and `circle_seed_rule_rebuild` maintenance-mode rows while still finding `0` human-edit-minute fields, so maintenance-savings claims are not ready. The private Theseus-Hive side now has `scripts/hive_record_maintenance_effort.py` to write measured human-edit rows, but none are present in the current aggregate run. These record real scored phase, mixer, router-head attachment, trainer-shadow, provenance-regeneration, source-change stress, workflow-rebuild ablations, and effort instrumentation, but they are not deployed-model, universal-compression, human-time, runtime, memory, or promotion evidence. The next private work should add harder contrastive route/ranker and router-head cases, implementation profiling, and measured human-edit minutes only on paired object-only versus Circle maintenance rows.

## Looped And Recursive Transformer Lane

The 2026-06-06 source review and 2026-06-07 online update are archived at `circle_calculus_codex_handoff/source_logs/06_looped_recursive_transformer_research.md`. They cover Universal Transformers, linear-attention recurrence, Recurrent Memory Transformer, looped transformers for learning algorithms, latent reasoning, and length generalization, RWKV, Mamba, LoopFormer, SpiralFormer, depth-recurrent reasoning, token-level Mixture-of-Recursions, middle-block recurrence, multi-resolution recurrence, recurrence-equivalence scaling laws, sparse/MoE looped models, and training-free loop wrappers.

The Circle Calculus opportunity is narrow and useful:

- treat loop step as an explicit finite phase,
- treat recurrence depth as a schedule with a budget and closure/exit status,
- record loop-state provenance instead of hiding it in an architecture diagram,
- measure overthinking boundaries where extra loops degrade a metric,
- compare recurrence schedules against ordinary fixed-depth, adaptive-exit, recurrent-memory, sparse/MoE, state-space, and dense transformer baselines.

The first implementation target is `P5-EDGE-010`, now seeded by `AIM-B0003`, `AIM-B0011`, `AIM-B0005`, `AIM-B0012`, `AIM-B0006`, `AIM-B0007`, `AIM-B0013`, `AIM-B0008`, `AIM-B0014`, and `AIM-B0009`: deterministic recurrence-schedule, loop-exit certificate, token-level recurrence routing, learned token-level recurrence routing, training-free loop-wrapper, middle-block recurrence, learned middle-block recurrence, multi-resolution recurrence, learned multi-resolution recurrence, and learned recurrence-schedule fixtures. The adjacent coil-attention lane now includes `AIM-B0010`, a deterministic learned content-gate fixture with route accuracy, wrong-period/flipped-gate controls, and candidate-budget accounting. These fixtures report loop budget, exit step, score trace, exit availability, overthinking guardrail status, active-token counts, selected middle block, resolution labels, wrong-period and wrong/over-loop controls, CPU/optional-MLX scoring, block-pass accounting, single-resolution controls, wrong-resolution controls, learned token phase-to-budget lookup tables, learned block phase lookup tables, learned resolution lookup tables, learned schedule lookup tables, learned phase-to-route lookup tables, and baseline labels before any MLX model training begins. Lean theorem targets should stay at finite schedule/index/closure facts unless a stronger formal model is explicitly built.

## First Demonstrators

The first useful artifacts should be small enough to verify end to end.

1. Proof-carrying circle diagrams for modular arithmetic and prime structure.
   Input examples: `C_13` with stride `5`, `C_36` with stride `8`.
   Output: visual orbit, period calculation, gcd certificate, Lean theorem link, human explanation, and machine-checkable proof.

2. Coil signatures for periodic data.
   Start with synthetic data before real data. Compute period candidates, closure profiles, prime-lag response, and antinode/interference maps. Compare against ordinary periodic baselines.

3. Mathematical knowledge browser.
   A glyph should expose visual form, formal definition, normal form, theorem dependencies, Lean proof, Python example, paper section, related glyphs, and higher-dimensional analogs.

## Post-S15 Pivot

The exceptional Hopf/division-algebra ladder ends at the `S^15` horizon:

```text
S^0 -> S^1  -> S^1
S^1 -> S^3  -> S^2
S^3 -> S^7  -> S^4
S^7 -> S^15 -> S^8
```

After `S^15`, do not chase a false classical `S^15 -> S^31 -> S^16` Hopf/division-algebra continuation. Higher spheres can exist in a general suspension or spectrum layer, but the next main phase should pivot from special objects to structured transformations.

Phase II north star:

```text
Circle Math Phase II:
From Dimensional Objects To Structured Transformations
```

Phase II programs:

- Stable sphere calculus: suspension, stable maps, spectra, and stable invariants.
- Bott/Clifford periodicity calculus: the dimension clock, real Clifford periodicity, spinors, K-theory, and KO-theory.
- Fiber/bundle proof calculus: base, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance.
- Boundary/cobordism calculus: boundary operators, `boundary(boundary)=0`, proofs as transformations between boundaries, and field/TQFT-adjacent structure.
- Circle/coil data analysis: practical data applications for periodic, recurrent, phase-like, and fibered structure.
- Proof-carrying glyph interface: visual, symbolic, executable, searchable, and formally checked theorem objects.
- Compositional systems layer: categories and functors connecting circles, coils, spheres, bundles, glyphs, proofs, fields, and data shapes.

Current active Phase II proof seed:

- `PAPER_P2_01_STABLE_SPHERE_CALCULUS` proves the finite double/four/eight suspension facts `P2S-T0001` through `P2S-T0005` in Lean through `Circle.Phase2.doubleSuspensionEuler`, `Circle.Phase2.fourSuspensionEuler`, `Circle.Phase2.fourSuspensionCounts_eq_double_double`, `Circle.Phase2.eightSuspensionCounts_eq_four_four`, and `Circle.Phase2.eightSuspensionEuler`, with matching Python examples.
- This is deliberately finite cell-count bookkeeping. It is the entry point for stable-sphere calculus, not a proof of spectra, stable maps, Bott periodicity, or stable homotopy groups.
- `PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY` proves the finite period-8 clock facts `P2B-T0001` through `P2B-T0004` in Lean through `Circle.Phase2.bottClockIndex_lt_eight`, `Circle.Phase2.bottClockIndex_add_eight`, `Circle.Phase2.bottClockIndex_zero`, and `Circle.Phase2.bottClockIndex_add_mul_eight`, with matching Python examples.
- This clock is roadmap bookkeeping for future Clifford/Bott work, not a proof of Clifford algebras, K-theory, KO-theory, or Bott periodicity.
- `PAPER_P2_03_BUNDLE_CALCULUS` proves the trivial product-bundle projection/fiber and base-preserving transition facts `P2BU-T0001` through `P2BU-T0009` in Lean through `Circle.Phase2.trivialBundleProjection_point`, `Circle.Phase2.trivialBundleFiber_point`, `Circle.Phase2.trivialBundleProjection_forgetsFiber`, `Circle.Phase2.trivialBundleFiber_forgetsBase`, `Circle.Phase2.bundleTransitionProjection_apply`, `Circle.Phase2.bundleTransitionFiber_apply`, `Circle.Phase2.bundleTransitionApply_compose`, `Circle.Phase2.bundleTransitionApply_identity`, and `Circle.Phase2.bundleTransitionApply_compose_identity`, with matching Python examples.
- This is base/fiber/transition vocabulary for later work, not a proof that Hopf fibrations or other twisted bundles are globally products, nor a cocycle/connection/curvature theorem.
- `PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS` proves the directed-interval boundary facts `P2BC-T0001` through `P2BC-T0005` in Lean through `Circle.Phase2.boundaryBoundaryInterval_zero`, `Circle.Phase2.intervalBoundary_reverse`, `Circle.Phase2.reverseInterval_involutive`, `Circle.Phase2.intervalBoundary_constant_zero`, and `Circle.Phase2.intervalBoundary_between_add`, with matching Python examples.
- This is finite boundary bookkeeping, not a proof of general chain complexes, cobordism, TQFT, or physics boundary laws.
- `PAPER_P2_05_PROOF_CARRYING_GLYPHS` proves the proof-glyph certificate projection, finite metadata-validity, and manifest-growth facts `P2G-T0001` through `P2G-T0006` in Lean through `Circle.Phase2.proofGlyphTheoremId_mk`, `Circle.Phase2.proofGlyphLeanName_mk`, `Circle.Phase2.proofGlyphGlyphId_mk`, `Circle.Phase2.proofGlyphValidAgainst_resolves_metadata`, `Circle.Phase2.proofGlyphValidAgainst_of_matching_metadata`, and `Circle.Phase2.proofGlyphValidAgainst_cons`, with matching Python examples.
- This is the metadata contract for proof-carrying diagrams, not a proof of glyph semantics, normal forms, generated-JSON parsing, dependency correctness, or proof search.
- `PAPER_APP_01_COIL_DATA_ANALYSIS` proves the finite phase-coordinate facts `APPD-T0001` through `APPD-T0005` in Lean through `Circle.Applications.phaseCoordinate_lt_period`, `Circle.Applications.phaseCoordinate_add_period`, `Circle.Applications.phaseCoordinate_zero`, `Circle.Applications.phaseCoordinate_add_mul_period`, and `Circle.Applications.phaseCoordinate_idempotent`, with matching Python examples. It also includes exploratory Python fixtures `APPD-B0001` and `APPD-B0002`, comparing coil closure ranking with autocorrelation and periodogram-style baselines on deterministic clean, noisy, aliased, and multi-period synthetic signals.
- This is a synthetic periodic-data primitive plus a first benchmark fixture, not a real-data period detector or evidence that coil closure beats ordinary baselines.
- `PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION` proves the cyclic-address facts `COMPC-T0001` through `COMPC-T0005` in Lean through `Circle.Applications.cyclicAddress_lt_size`, `Circle.Applications.cyclicAddress_add_size`, `Circle.Applications.cyclicAddress_zero`, `Circle.Applications.cyclicAddress_add_mul_size`, and `Circle.Applications.cyclicAddress_idempotent`, with matching Python examples.
- This is a proof-carrying rewrite primitive, not evidence that any backend is faster.
- `PAPER_COMP_02_COIL_RAY_AND_SAMPLING` proves the direction-bin schedule facts `COMPR-T0001` through `COMPR-T0005` in Lean through `Circle.Applications.directionBin_lt_binCount`, `Circle.Applications.directionBin_add_binCount`, `Circle.Applications.directionBin_zero`, `Circle.Applications.directionBin_add_mul_binCount`, and `Circle.Applications.directionBin_idempotent`, with matching Python examples.
- This is finite queue/sampler indexing, not evidence of ray-coherence speedup, lower noise, or better frame time.
- `PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT` proves the stride-address facts `COMPL-T0001` through `COMPL-T0005` in Lean through `Circle.Applications.strideAddress_lt_size`, `Circle.Applications.strideAddress_add_size_steps`, `Circle.Applications.strideAddress_zero_step`, `Circle.Applications.strideAddress_zero_stride`, and `Circle.Applications.strideAddress_add_mul_size_steps`, with matching Python examples and the exploratory CPU/optional-MLX CoilLayout validation/benchmark-grid fixture `COMPL-B0001` plus the periodic-boundary stencil validation fixture `COMPL-B0002`.
- This is address-level structure plus a starter benchmark scaffold with expected-output checks, not a proof of cache locality, stencil correctness, NTT correctness, or backend speed.
- `PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS` proves the round-robin schedule facts `COMPS-T0001` through `COMPS-T0004` in Lean through `Circle.Applications.roundRobinSlot_lt_slotCount`, `Circle.Applications.roundRobinSlot_add_slotCount`, `Circle.Applications.roundRobinSlot_zero`, and `Circle.Applications.roundRobinSlot_add_mul_slotCount`, with matching Python examples.
- This is a finite scheduler primitive, not a fairness, load-balancing, robotics, ANN, codec, acquisition, CAM, torsion, detection, or quantum-computing theorem.
- `PAPER_AI_01_CIRCLE_AI_ARCHITECTURES` proves the phase-channel facts `AIA-T0001` through `AIA-T0005` in Lean through `Circle.Applications.phaseChannel_lt_period`, `Circle.Applications.phaseChannel_add_period`, `Circle.Applications.phaseChannel_zero`, `Circle.Applications.phaseChannel_add_mul_period`, and `Circle.Applications.phaseChannel_idempotent`, with matching Python examples plus the exploratory deterministic benchmark fixtures `AIA-B0001`, `AIA-B0002`, `AIA-B0003`, `AIA-B0004`, and `AIA-B0005`.
- `PAPER_AI_02_COIL_ATTENTION_AND_MEMORY` proves the cyclic-memory-slot, finite loop-schedule, active-token-step, middle-block-route, multi-pass recurrence closure, training-free loop-budget, unavailable-budget clamp, overthinking-boundary, loop-exit certificate, certificate-availability, and certificate-budget-selection facts `AIM-T0001` through `AIM-T0043` in Lean, with matching Python examples plus the exploratory cyclic-memory benchmark fixture `AIM-B0001`, the exploratory coil-retrieval reachability fixture `AIM-B0002`, the exploratory looped-recurrence schedule fixture `AIM-B0003`, the exploratory content-gated retrieval fixture `AIM-B0004`, the exploratory token-level recurrence routing fixture `AIM-B0005`, the exploratory training-free loop-wrapper fixture `AIM-B0006`, the exploratory middle-block recurrence fixture `AIM-B0007`, the exploratory multi-resolution recurrence fixture `AIM-B0008`, the exploratory learned recurrence-schedule fixture `AIM-B0009`, the exploratory learned content-gate retrieval fixture `AIM-B0010`, the exploratory loop-exit certificate fixture `AIM-B0011`, the exploratory learned token-level recurrence fixture `AIM-B0012`, the exploratory learned middle-block recurrence fixture `AIM-B0013`, and the exploratory learned multi-resolution recurrence fixture `AIM-B0014`.
- `PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE` proves the adapter-block facts `AIRA-T0001` through `AIRA-T0005` in Lean through `Circle.Applications.adapterBlock_lt_blockSize`, `Circle.Applications.adapterBlock_add_blockSize`, `Circle.Applications.adapterBlock_zero`, `Circle.Applications.adapterBlock_add_mul_blockSize`, and `Circle.Applications.adapterBlock_idempotent`, with matching Python examples plus the exploratory adapter-block benchmark fixture `AIRA-B0001`, the exploratory MultiCoil/RoPE-style positional fixture `AIRA-B0002`, the exploratory RoPE-style relative phase fixture `AIRA-B0003`, the exploratory adapter parameter-budget fixture `AIRA-B0004`, and the exploratory circulant-mixer validation fixture `AIRA-B0005`.
- These are finite indexing primitives for AI prototypes plus starter phase-channel, learned-feature baseline, harmonic-feature baseline, backend-parity, cyclic-memory, coil-retrieval, content-gated retrieval, learned content-gate retrieval, looped-recurrence, token-level recurrence, learned token-level recurrence, training-free loop-wrapper, middle-block recurrence, learned middle-block recurrence, multi-resolution recurrence, learned multi-resolution recurrence, learned recurrence-schedule, adapter-block, MultiCoil positional, and relative phase harnesses, not model-quality, parameter-efficiency, attention-replacement, RoPE, retrieval, recursive-reasoning, or runtime claims.

## Compute Track

The compute thesis is narrow:

Circle Math will not make arbitrary computation faster. It can help when an operation really has cyclic, circulant, convolutional, rotational, periodic, or fibered structure.

The opportunity is proof-carrying circular computation:

```text
Circle/coil expression
  -> Lean proof of cyclic/circulant/orbit structure
  -> theorem manifest records a legal rewrite
  -> compiler/runtime lowers to a specialized backend
  -> benchmark verifies whether the rewrite is actually faster
```

Current local backend policy:

- This machine is Mac-first. Use MLX and other Apple-compatible paths for local accelerator experiments.
- Do not write CUDA-only code for the active local pipeline.
- CUDA, cuFFT, and NVIDIA-specific libraries may appear only as future portability notes or external benchmark baselines.
- Exact finite arithmetic and NTT work should start in Python/Lean with CPU reference implementations unless an Apple-compatible integer-transform backend is selected.

Compute tracks to add only after the proof/math roadmap is stable enough:

- Proof-carrying circular computation.
- MLX coil layout optimization.
- FFT/NTT backends for certified circle operators.
- Block-circulant neural layers.
- Spherical and hyperspherical compute kernels.
- Quaternion orientation pipelines.

First compute experiments:

1. Dense vs circulant matrix-vector multiplication.
   Compare dense `A x` with FFT-style circular convolution for increasing `n` and batch sizes. Measure runtime, memory, numerical error, and backend overhead.

2. Coil-order memory layout.
   Compare natural order with orbit-order layout for stride updates `x[i] <- f(x[i], x[i+k mod n])`, using gcd-cycle decomposition for composite `n`.

3. Finite-circle cyclic convolution and NTT reference.
   Compare direct convolution, FFT convolution, and exact modular convolution. Keep NTT exactness and modulus constraints explicit.

## Circle Compute And Systems Applications

The non-AI compute handoff should be preserved as application context, not as proved math. The rule is the same as the main compute track: Circle Math helps only where the workload has real cyclic, angular, periodic, spherical, toroidal, rotational, circulant, or ring-buffer structure.

Most promising prototype families:

- `CoilRay Sort`: ray/path tracing reordering by spherical-coil direction bins, material class, and approximate BVH region to improve ray coherence.
- `CoilSampler`: deterministic circle/sphere/hemisphere sampling through golden-angle, spherical Fibonacci, and coprime latitude/longitude schedules with explicit coverage and alias diagnostics.
- `CoilNoise`: procedural placement, dithering, particle emission, starfields, lens sampling, and other deterministic progressive sample sequences generated from irrational or coprime orbits.
- `CoilLayout`: memory layouts for strided circular updates `i -> i + k mod n`, using orbit order and gcd-cycle decomposition.
- `CoilStencil`: periodic-boundary stencil compilation that can choose direct stencil, FFT, block-circulant, or coil-layout backends with verified wraparound.
- `CoilNTT`: exact finite-circle transform tooling for cyclic convolution, polynomial rings, FHE, ZK systems, and NTT butterfly layouts.
- `CoilHash`: consistent-hashing extensions using multi-ring placement, coprime virtual nodes, hotspot/antinode detection, and remapping proofs.
- `CoilMotion`: phase-aware game/animation loops, motion matching, quaternion orientation blending, and derivative-closed cycles.
- `CoilPRM` / `CoilRRT`: robotics samplers for toroidal joint spaces and `S^3` orientation states.
- `CoilCodec`: phase-aware audio/video compression and loop detection.
- `CoilANN`: angular/hash-ring vector indexing through projections into products of circles.

Additional systems domains to keep in view:

- Scientific instruments: `CoilAcquire` for CT, MRI, radar, lidar, sonar, radio astronomy, angular scan scheduling, alias avoidance, phase unwrapping, and spherical sensor fusion.
- Geometry/CAD/3D printing: `CoilCAM` for closed-loop mesh repair, seam-aware UVs, spiral or coil infill, and continuous toolpaths.
- Molecular simulation and biology: `CoilTorsion` for torsion angles, protein conformer sampling, periodic boxes, and rotationally equivariant features.
- Cybersecurity and anomaly detection: `CoilDetect` for daily/weekly phase features, beaconing, cron rhythms, heartbeat drift, and cycle-breaking anomaly scores.
- Operating systems and runtime schedulers: `CoilSched` for round-robin fairness, ring buffers, timer wheels, stride schedules, and gcd-based starvation diagnostics.
- Quantum circuits: `CoilQ` for phase-gate normal forms, Bloch-sphere views, `SU(2)`/quaternion-style rotation reasoning, and circuit identity search.

The strongest first three from the handoff are:

1. `CoilRay Sort`, because ray coherence is a real rendering bottleneck.
2. `CoilLayout`, because memory-layout improvements are practical and measurable.
3. `CoilNTT`, because exact cyclic transforms are core workloads in cryptography, FHE, ZK systems, and polynomial computation.

The latest compute handoff also ranks `CoilSampler`, `CoilStencil`, `CoilHash`, `CoilMotion`, `CoilPRM`, `CoilCodec`, and `CoilANN` as worth prototyping after the first three. Keep these as benchmark tracks until a specific workload, baseline, and measurement plan exist.

Latest 2026-06-05 compute handoff ranking:

1. `CoilRay Sort`: ray/path tracing reordering by spherical-coil direction bins.
2. `CoilSampler`: deterministic sphere/hemisphere sampling and progressive Monte Carlo schedules.
3. `CoilLayout`: orbit-order and gcd-cycle memory layouts for strided circular updates.
4. `CoilStencil`: periodic-boundary simulation/PDE stencil lowering with verified wraparound.
5. `CoilNTT`: exact finite-circle transform tooling for cyclic convolution, ZK, FHE, and polynomial workloads.
6. `CoilHash`: multi-ring consistent hashing, hotspot diagnostics, and remapping proofs.
7. `CoilMotion`: phase-aware animation loops, motion matching, and quaternion orientation blending.
8. `CoilPRM` / `CoilRRT`: torus and `S^3` samplers for robotics configuration spaces.
9. `CoilCodec`: phase-aware audio/video compression and loop detection.
10. `CoilANN`: angular/hash-ring vector indexing through products of circles.

The same handoff frames the largest application as `CoilIR`: a proof-carrying optimizer for cyclic, angular, and periodic computation. The intended pipeline is dictionary-recognized circular structure, Lean-proved rewrites or address transformations, backend choices such as FFT, NTT, spherical harmonics, quaternion kernels, coiled layouts, ring buffers, ray buckets, or samplers, and benchmarks that decide whether the backend is actually worthwhile.

First rendering experiment:

```text
baseline wavefront path tracer
direction-bucketed path tracer
spherical-coil-bucketed path tracer
```

At each bounce, map `ray.direction` to an `S^2` bin, map that bin to a coil index, bucket the ray queue, and measure rays per second, cache behavior, divergence, BVH traversal time, noise per sample, and total frame time. The hypothesis is only that spherical-coil bucketing may improve coherence with less overhead than a heavier general sort. If benchmarks fail, record the failure and keep the theorem/proof layer separate from performance claims.

Long-term meta-application:

```text
human/model operation
  -> Circle dictionary identifies cyclic/angular structure
  -> Lean proves the rewrite or address transformation
  -> CoilIR chooses FFT, NTT, spherical harmonics, quaternion kernels, coiled layouts, ring buffers, ray buckets, or samplers
  -> benchmarks decide whether the backend is worthwhile
```

Compute caveats:

- Dense GEMM and tensor kernels are heavily optimized; structured methods win only when the structure is real enough.
- FFT overhead can dominate small problems.
- Prime circle sizes are mathematically clean, but smooth composite sizes can be faster for transforms.
- Hardware-aware circle selection is a design axis, not a contradiction.
- Benchmarks decide performance claims.

## Circle AI Track

The AI thesis is narrow and benchmark-driven:

Circle Math does not imply that circles improve every neural network. It may help when model structure or data structure is cyclic, periodic, convolutional, rotational, harmonic, recurrent, memory-like, or proof-search-like.

Many existing AI components already have circle-shaped pieces:

- RoPE and rotary embeddings: position as rotation/phase.
- Fourier neural operators and FFT-based sequence mixers: learning or mixing in frequency space.
- SIREN and periodic activations: sinusoidal primitives for signals and neural fields.
- Circulant and block-circulant neural layers: matrix rows generated by rotations.
- Long convolution systems such as Hyena-like mixers: sequence mixing through convolutional structure.
- Structured state-space models such as S4/Mamba-like systems: long-range recurrence through structured dynamics.
- Spherical CNNs: equivariant models on `S^2` and `SO(3)`.
- Quaternion neural networks: `S^3`-like feature coupling where orientation or grouped channels matter.

The possible contribution is not inventing those ingredients. The possible contribution is a circle/coil-native architecture and compiler layer that makes phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, and proof-carrying structure systematic.

Deferred Circle AI subprojects:

- Coil Attention: sparse attention through selected strides, coprime coverage, gcd/orbit reasoning, and hybrid local/global/content-gated attention.
- Coil Memory / CoilKV: long-context circular memory banks with residue, winding, alias control, learned gates, and retrieval along coil paths.
- CoilLinear / CoilRA: circulant or block-circulant neural layers and adapters, optionally combined with low-rank adaptation.
- MultiCoil RoPE: generalized rotary embeddings with multiple periods, coprime phases, winding-aware features, and torus-valued position views.
- Periodic activation systems: learned period lattices, prime-frequency bases, closure penalties, and fibered phase channels.
- Spherical/quaternion AI: `S^2` equivariant models and `S^3` quaternion/orientation models where the data has that geometry.
- Activation coil analysis: model-internal trajectories, repeated circuits, closure patterns, attention-head coil motifs, and failure-mode aliasing.
- AI theorem proving and proof search: dictionary terms, theorem ids, glyph normal forms, Lean declarations, proof dependencies, and shape-native hints for cyclic/modular domains.

First Circle AI prototypes:

1. Phase-channel learned-task benchmarks built from `AIA-B0001` and `AIA-B0002`.
   Use `AIA-B0003` as backend parity scaffolding, `AIA-B0004` as learned-feature baseline scaffolding, and `AIA-B0005` as harmonic/Fourier-feature scaffolding while expanding from scalar/position/wrong-frequency controls to standard RoPE, dense learned, and MLX model baselines before making model-quality claims.

2. Coil Attention plus MultiCoil RoPE on synthetic long-context retrieval.
   Start from `AIM-B0002` as the coil-retrieval reachability scaffold, `AIRA-B0002` as the MultiCoil/RoPE-style positional scaffold, and `AIRA-B0003` as the relative phase scaffold only. Compare against full attention, standard RoPE, learned positional encodings, sliding window, dilated attention, BigBird-like sparse attention, Hyena-like long convolution, and S4/Mamba-like state-space baselines.

3. CoilRA adapters for small language-model fine-tuning.
   Start from `AIRA-B0001` as the adapter-block scaffold only. Compare against dense adapters, LoRA, and block-circulant baselines. Measure quality, parameter count, inference cost, and MLX runtime on this Mac.

4. CoilKV memory for streaming sequence models.
   Compare against KV cache, recurrent summaries, retrieval buffers, and state-space baselines. Measure collision/alias behavior explicitly.

5. Activation coil analysis on trained transformer checkpoints.
   Look for closure patterns, induction-like circuits, attention-head coil motifs, repeated reasoning loops, and whether alias/closure diagnostics predict failures.

6. Theseus-Hive transfer.
   Use `docs/THESEUS_HIVE_AI_TRANSFER.md`, `P5-EDGE-011`, and `site/data/generated/theseus_hive_ai_contracts.json` as the bridge from Circle AI to the user's active AI system. The public Circle-side contract fixtures now cover recurrence schedules, strided fanout coverage, cyclic memory, phase tags, circulant/block-cyclic mixers, and seed-rule provenance. The companion Theseus-Hive workspace now has report-only consumers that load those fixtures and emit YELLOW private-planning, structural-smoke, deterministic-proxy, aggregate real-workload attachment, scored candidate-manifest, semantic score-context, full-frontier equal-budget semantic, recurrence work-budget, context-memory, phase-feature, route-mixer, router-head attachment, seed-rule, seed-rule stress, workflow-rebuild, and update-cycle effort reports with zero external inference, no training mutation, no promotion evidence, six named smoke workload slots, six proxy benchmark ids, six aggregate local-artifact attachment ids, three scored fanout ids, one scored recurrence id, one scored memory id, one scored phase id, two scored mixer ids, one scored seed-rule id, one scored seed-rule stress id, one scored workflow-rebuild id, and one update-cycle effort instrumentation id: `circle_candidate_fanout_scored_manifest_v1`, `circle_candidate_fanout_semantic_frontier_v1`, `circle_candidate_fanout_equal_budget_semantic_v1`, `circle_recurrence_work_budget_semantic_v1`, `circle_memory_context_packet_retrieval_v1`, `circle_phase_feature_sequence_ablation_v1`, `circle_mixer_route_ranker_ablation_v1`, `circle_mixer_router_head_attachment_v1`, `circle_seed_rule_exact_regeneration_v1`, `circle_seed_rule_source_change_stress_v1`, `circle_seed_rule_workflow_tool_card_rebuild_v1`, and `circle_seed_rule_update_cycle_effort_v1`. The full-frontier semantic and recurrence runs both score 1040 private tasks across 26 categories but tie ordinary rank-one/fixed-depth baselines; the memory run scores 37 context-packet targets but equal-budget Circle retention ties ordinary retention baselines; the phase run ties no-phase/wrong-period controls; the mixer run ties dense heldout trace accuracy with lower counted parameters on a small route/ranker fixture; the router-head attachment run ties current router-head agreement with the same lower counted Circle parameter budget; the actual Octopus router-head trainer now has `circle_router_head_mixer_shadow_training_v1`, an opt-in `--circle-mixer circulant|block_cyclic|circulant_residual|block_cyclic_residual` aggregate shadow benchmark that ties the no-mixer trainer at 14/14 holdout exact-set accuracy with zero external inference on current local traces and records 5-repetition stable timing across pure and residual Circle modes with median elapsed 8.926 ms baseline, 105.975 ms pure circulant, 110.399 ms pure block-cyclic, 104.434 ms residual circulant, and 112.164 ms residual block-cyclic plus median Python-traced peak bytes 117078, 335105, 338973, 447449, and 438130; its keyword-boundary contrastive diagnostic has 45 holdout examples where full-gain pure and residual Circle modes still trail the no-mixer baseline, while a quality-only gain sweep finds bounded residual gains 0.05, 0.1, 0.25, and 0.5 preserve synthetic baseline exactness; the seed-rule exact run exactly regenerates 75 safe provenance-envelope records with zero verifier residuals using a shorter source/rule recipe than object-only storage; the seed-rule stress run applies 4 deterministic source-change scenarios with 20 downstream reuse queries, tying object-only exactness and reuse while recording lower average description length and edit cost; the workflow/tool-card rebuild run reads 72 safe sources and rebuilds 188 safe envelope records while recording lower automated rebuild work units than object-only storage; and the update-cycle effort run now finds paired object-only and Circle maintenance-mode rows while still lacking measured human-edit-minute fields. These are not deployed-model or broad Circle advantage claims; next design selection, recurrence, memory, phase, mixer, or trainer-shadow workloads that differ from ordinary baselines when evidence supports them and use the measured-effort recorder before claiming maintenance usefulness.

Circle AI guardrails:

- Do not replace all attention with fixed circles. Start with hybrid local, global, coil, and content-gated components.
- Do not use prime sizes everywhere. Mix prime/coprime reasoning with hardware-friendly smooth sizes.
- Do not start with octonion AI. Stage `S^1` phase, then `S^3` quaternion/orientation models; keep `S^7` exploratory until the math and benchmarks justify it.
- Do not claim general AI improvement. The target is cheaper, more interpretable, or more geometry-aware components in domains where cyclic or harmonic structure is real.
- Do not claim Circle Calculus has improved Theseus-Hive until a named Theseus-Hive workload, baseline, metric, script, and report support that claim.
- Use MLX/Mac-compatible prototypes first in this local project. CUDA references remain external baselines or future portability notes.

## Planned And Active Scaffolds Created

These files exist so later Phase II and application work has stable paper and manifest anchors. `PAPER_P2_01_STABLE_SPHERE_CALCULUS` through `PAPER_P2_05_PROOF_CARRYING_GLYPHS`, `PAPER_APP_01_COIL_DATA_ANALYSIS`, `PAPER_COMP_01` through `PAPER_COMP_04`, and `PAPER_AI_01` through `PAPER_AI_03` are active proof seeds; benchmark claims still require benchmark artifacts.

Planned manifests:

- `manifests/theories/stable_sphere_calculus.yaml`
- `manifests/theories/bott_clifford_calculus.yaml`
- `manifests/theories/bundle_calculus.yaml`
- `manifests/theories/boundary_cobordism_calculus.yaml`
- `manifests/theories/glyph_proof_interface.yaml`
- `manifests/applications/coil_data_analysis.yaml`
- `manifests/applications/coil_compute.yaml`
- `manifests/applications/coil_rendering.yaml`
- `manifests/applications/coil_systems.yaml`
- `manifests/applications/circle_ai.yaml`

Planned and active paper anchors:

- `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md`
- `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md`
- `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md`
- `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md`
- `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md`
- `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md`
- `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md`
- `papers/applications/PAPER_COMP_02_COIL_RAY_AND_SAMPLING.md`
- `papers/applications/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT.md`
- `papers/applications/PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS.md`
- `papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md`
- `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`
- `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md`

## Reference Pointers From Handoffs

These sources were named in the browser handoffs as orientation material. They should be verified before being used as formal bibliography entries in a paper.

- Baez, "The Octonions": `https://arxiv.org/abs/math/0105155`
- Adams, "On the Non-Existence of Elements of Hopf Invariant One": `https://www.sas.rochester.edu/mth/sites/doug-ravenel/otherpapers/Adams-HI1.pdf`
- Isaksen, Wang, and Xu, "Stable homotopy groups of spheres": `https://www.pnas.org/doi/10.1073/pnas.2012335117`
- Fong and Spivak, "Seven Sketches in Compositionality": `https://arxiv.org/abs/1803.05316`
- Persistent cohomology and circular coordinates: `https://arxiv.org/abs/0905.4887`
- Spherical CNNs: `https://arxiv.org/abs/1801.10130`
- MIT notes on Toeplitz/circulant FFT multiplication: `https://math.mit.edu/icg/resources/teaching/18.085-spring2015/toeplitz.pdf`
- GPU NTT reference from the handoff: `https://eprint.iacr.org/2021/124`
- RoFormer / RoPE: `https://arxiv.org/abs/2104.09864`
- Circulant neural networks: `https://arxiv.org/abs/1708.08917`
- FlashAttention: `https://arxiv.org/abs/2205.14135`
- Longformer: `https://arxiv.org/abs/2004.05150`
- Hyena Hierarchy: `https://arxiv.org/abs/2302.10866`
- S4 structured state spaces: `https://arxiv.org/abs/2111.00396`
- LoRA: `https://arxiv.org/abs/2106.09685`
- SIREN periodic activations: `https://arxiv.org/abs/2006.09661`
- Deep Quaternion Networks: `https://arxiv.org/abs/1712.04604`
- NVIDIA ray tracing overview: `https://developer.nvidia.com/discover/ray-tracing`
- NVIDIA wavefront path tracing handoff reference: `https://research.nvidia.com/sites/default/files/pubs/2013-07_Megakernels-Considered-Harmful/laine2013hpg_paper.pdf`
- Ray reordering handoff reference: `https://arxiv.org/html/2506.11273v1`
- Spherical Fibonacci point sets handoff reference: `https://ribardiere.pages.xlim.fr/articles/2013/CGF_SF.pdf`
- ReSTIR handoff reference: `https://research.nvidia.com/sites/default/files/pubs/2020-07_Spatiotemporal-reservoir-resampling/ReSTIR.pdf`
- Precomputed radiance transfer handoff reference: `https://cseweb.ucsd.edu/~ravir/6998/papers/p527-sloan.pdf`
- Consistent hashing handoff reference: `https://www.cs.princeton.edu/courses/archive/fall07/cos518/papers/chash.pdf`
