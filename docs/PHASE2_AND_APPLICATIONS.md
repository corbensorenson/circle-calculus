# Phase II And Application Tracks

This note preserves the application and post-`S^15` context from the browser handoffs without turning the repository into a transcript archive. The canonical operating checklist remains `docs/COMPLETION_ROADMAP.md`.

None of this file changes proof status. A claim is proved only when it has a compiled Lean declaration and passes the repository proof checks.

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

- `PAPER_P2_01_STABLE_SPHERE_CALCULUS` proves the finite double/four suspension Euler facts `P2S-T0001` and `P2S-T0002` in Lean through `Circle.Phase2.doubleSuspensionEuler` and `Circle.Phase2.fourSuspensionEuler`.
- This is deliberately finite cell-count bookkeeping. It is the entry point for stable-sphere calculus, not a proof of spectra, stable maps, Bott periodicity, or stable homotopy groups.
- `PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY` proves the finite period-8 clock facts `P2B-T0001` and `P2B-T0002` in Lean through `Circle.Phase2.bottClockIndex_lt_eight` and `Circle.Phase2.bottClockIndex_add_eight`.
- This clock is roadmap bookkeeping for future Clifford/Bott work, not a proof of Clifford algebras, K-theory, KO-theory, or Bott periodicity.
- `PAPER_P2_03_BUNDLE_CALCULUS` proves the trivial product-bundle projection/fiber facts `P2BU-T0001` through `P2BU-T0003` in Lean through `Circle.Phase2.trivialBundleProjection_point`, `Circle.Phase2.trivialBundleFiber_point`, and `Circle.Phase2.trivialBundleProjection_forgetsFiber`.
- This is base/fiber vocabulary for later work, not a proof that Hopf fibrations or other twisted bundles are globally products.

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

1. Coil Attention plus MultiCoil RoPE on synthetic long-context retrieval.
   Compare against full attention, sliding window, dilated attention, BigBird-like sparse attention, Hyena-like long convolution, and S4/Mamba-like state-space baselines.

2. CoilRA adapters for small language-model fine-tuning.
   Compare against dense adapters, LoRA, and block-circulant baselines. Measure quality, parameter count, inference cost, and MLX runtime on this Mac.

3. CoilKV memory for streaming sequence models.
   Compare against KV cache, recurrent summaries, retrieval buffers, and state-space baselines. Measure collision/alias behavior explicitly.

4. Activation coil analysis on trained transformer checkpoints.
   Look for closure patterns, induction-like circuits, attention-head coil motifs, repeated reasoning loops, and whether alias/closure diagnostics predict failures.

Circle AI guardrails:

- Do not replace all attention with fixed circles. Start with hybrid local, global, coil, and content-gated components.
- Do not use prime sizes everywhere. Mix prime/coprime reasoning with hardware-friendly smooth sizes.
- Do not start with octonion AI. Stage `S^1` phase, then `S^3` quaternion/orientation models; keep `S^7` exploratory until the math and benchmarks justify it.
- Do not claim general AI improvement. The target is cheaper, more interpretable, or more geometry-aware components in domains where cyclic or harmonic structure is real.
- Use MLX/Mac-compatible prototypes first in this local project. CUDA references remain external baselines or future portability notes.

## Planned And Active Scaffolds Created

These files exist so later Phase II and application work has stable paper and manifest anchors. Most remain planned scaffolds rather than proof claims; `PAPER_P2_01_STABLE_SPHERE_CALCULUS`, `PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY`, and `PAPER_P2_03_BUNDLE_CALCULUS` are the first active Phase II proof seeds.

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
