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

Compute caveats:

- Dense GEMM and tensor kernels are heavily optimized; structured methods win only when the structure is real enough.
- FFT overhead can dominate small problems.
- Prime circle sizes are mathematically clean, but smooth composite sizes can be faster for transforms.
- Hardware-aware circle selection is a design axis, not a contradiction.
- Benchmarks decide performance claims.

## Deferred Scaffolding

Do not create these until the `S^1` through `S^15` horizon is stable or the active roadmap explicitly advances to Phase II.

Planned manifests:

- `manifests/theories/stable_sphere_calculus.yaml`
- `manifests/theories/bott_clifford_calculus.yaml`
- `manifests/theories/bundle_calculus.yaml`
- `manifests/theories/boundary_cobordism_calculus.yaml`
- `manifests/theories/glyph_proof_interface.yaml`
- `manifests/applications/coil_data_analysis.yaml`
- `manifests/applications/coil_compute.yaml`

Planned papers:

- `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md`
- `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md`
- `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md`
- `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md`
- `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md`
- `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md`
- `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md`

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
