# Circle Research Expansion Backlog

Research date: 2026-06-21.

Claim boundary: this is a research and implementation backlog. It does not add
new proved claims by itself. Every item below should enter the project through
the existing proof policy: paper/source trail, theorem manifest entry, Lean
sidecar where appropriate, executable fixture if useful, and explicit claim
boundary.

## Selection Rule

Add a topic when circles are structurally central, not decorative. Good
candidates satisfy at least two of:

- the circle group, roots of unity, cyclic order, winding, phase, or rotation is
  the core object;
- the topic has a small formal theorem spine that can be proved in Lean;
- the topic can produce a reusable Python/Rust library surface;
- the topic can produce a versioned contract artifact useful for AI/system
  engineering.

## Priority 0: Foundation Tracks

These should come before broad new theory because they unlock many downstream
applications.

### 1. Finite Fourier, Roots Of Unity, And Circulant Algebra

Why it belongs: a finite circle is a cyclic group. The Fourier basis is the
character table of that group, and circulant matrices are exactly the linear
maps controlled by cyclic shifts.

Sources:

- Mathlib defines the complex unit circle as a group/topological group and
  provides `Circle.exp`: <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Complex/Circle.html>
- Mathlib roots of unity includes `rootsOfUnity` and cyclicity results:
  <https://leanprover-community.github.io/mathlib4_docs/Mathlib/RingTheory/RootsOfUnity/Basic.html>
- Mathlib Fourier transform docs expose the translation-to-phase principle:
  <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Fourier/FourierTransform.html>
- Structured neural transforms use circulant/low-displacement structure for
  compact models: <https://arxiv.org/abs/1510.01722>
- CirCNN/block-circulant neural work shows direct AI relevance:
  <https://arxiv.org/abs/1708.08917>

Add:

- Lean: `Circle.Core.RootsOfUnity`, `Circle.Core.FiniteFourier`,
  `Circle.Applications.CirculantSpectral`.
- Prove: finite character periodicity, character multiplication,
  orthogonality of characters over `ZMod n`, circular convolution identity,
  circulant shift commutation, Fourier diagonalization of circulant operators.
- Python: `circle_math.harmonics` with DFT matrix, circular convolution,
  circulant matrix construction, spectral support, aliasing checks.
- Contracts: `circulant_layer_spectral_contract` and
  `spectral_aliasing_contract` for AI layers using circular convolution or
  block-circulant matrices.

First small Lean targets:

- `character_add`: `χ k (a + b) = χ k a * χ k b`
- `character_periodic`: `χ k (a + n) = χ k a`
- `cyclic_convolution_commutes_with_rotation`
- `circulant_apply_rotation_eq_rotation_apply_circulant`

### 2. Positional Encoding As Circle Phase Algebra

Why it belongs: sinusoidal and rotary position encodings are circle-valued phase
systems. This project already has RoPE contracts; the next step is to turn that
into a general "position-as-phase" library.

Sources:

- Transformer sinusoidal positional encodings: <https://arxiv.org/abs/1706.03762>
- RoFormer/RoPE: <https://arxiv.org/abs/2104.09864>
- ALiBi length extrapolation baseline to compare against:
  <https://arxiv.org/abs/2108.12409>
- xPos / length-extrapolatable Transformer:
  <https://arxiv.org/abs/2212.10554>
- YaRN RoPE extension: <https://arxiv.org/abs/2309.00071>
- LongRoPE non-uniform RoPE scaling: <https://arxiv.org/abs/2402.13753>
- 2D RoPE for vision transformers: <https://arxiv.org/abs/2403.13298>

Add:

- Lean: general phase-bank definitions independent of RoPE model naming.
- Python: `circle_math.position_phase` with sinusoidal PE, RoPE, xPos-style
  scaling descriptors, YaRN/LongRoPE schedule descriptors.
- Contracts: `phase_bank_collision_contract`,
  `scaled_rope_schedule_contract`, and `two_dimensional_rope_grid_contract`.
- Docs: separate proved integer-period facts from numerical/empirical
  length-extension claims.

First small Lean targets:

- phase-bank equality depends only on gap modulo each declared period;
- adding a channel cannot create a collision if a prefix already distinguishes;
- product/grid RoPE collision iff both axis phase banks collide;
- declared scaled schedule preserves positive periods under integer rounding.

### 3. Sparse Attention As Circle Graph Coverage

Why it belongs: local windows, strides, global tokens, and wraparound attention
patterns are graph reachability problems on a finite circle.

Sources:

- BigBird frames sparse attention as graph sparsification and emphasizes small
  path length plus locality: <https://arxiv.org/abs/2007.14062>
- Longformer combines local windowed attention with global attention:
  <https://arxiv.org/abs/2004.05150>
- Sparse Sinkhorn Attention uses learned permutations plus local windows:
  <https://arxiv.org/abs/2002.11296>

Add:

- Lean: `Circle.Applications.SparseAttentionGraph`.
- Prove: local-window reachability, stride-generator reachability, diameter
  bounds for circulant stride graphs, global-token two-hop coverage, monotonicity
  under adding edges.
- Python: coverage/diameter/connected-component analyzers for declared
  attention graphs.
- Contracts: `attention_graph_diameter_contract`,
  `attention_global_token_bridge_contract`, `permutation_bucket_coverage_contract`.

First small Lean targets:

- `local_window_edges_subset_added_window`
- `stride_edges_generate_subgroup`
- `gcd_strides_one_implies_connected_circulant_graph`
- `global_token_two_hop_reaches_all`

### 4. Circle-Valued Statistics And Directional Uncertainty

Why it belongs: angular error, pose, heading, phase, and direction are not real
line variables. Their natural statistics live on `S1` or higher spheres.

Sources:

- Directional statistics overview: <https://jammalam.faculty.pstat.ucsb.edu/html/Some%20Publications/2015_Directional%20Stats-Intro_WileyStatsRef.pdf>
- Mardia/Jupp directional statistics overview: <https://books.google.com/books/about/Directional_Statistics.html?id=zjPvAAAAMAAJ>
- CircStat toolbox paper: <https://www.jstatsoft.org/v31/i10>
- PyCircStat2 docs: <https://circstat.github.io/pycircstat2/>
- Deep directional statistics for pose uncertainty:
  <https://openaccess.thecvf.com/content_ECCV_2018/papers/Sergey_Prokudin_Deep_Directional_Statistics_ECCV_2018_paper.pdf>
- von Mises-Fisher analysis of SGD directions:
  <https://arxiv.org/abs/1810.00150>

Add:

- Lean: finite circular mean/resultant definitions for rational/complex unit
  samples where feasible; keep continuous distribution claims as docs until
  measure theory is worth the cost.
- Python: `circle_math.circular_stats` with angle wrapping, circular distance,
  resultant vector, circular mean, circular variance, von Mises log-likelihood
  helpers.
- Contracts: `angular_error_wrap_contract`,
  `pose_uncertainty_distribution_contract`,
  `phase_gradient_direction_contract`.

First small Lean targets:

- wrapped angular difference is invariant under adding full turns;
- circular distance is symmetric and bounded by half-turn;
- resultant of all identical phases points at that phase;
- rotating every sample rotates the resultant by the same angle.

## Priority 1: AI Architecture Tracks

### 5. Rotation Equivariance, Circular Harmonics, And Steerable Networks

Why it belongs: rotation equivariance is circle-group equivariance. Circular
harmonics are the character basis of `SO(2)`/`C_n`.

Sources:

- Group equivariant CNNs: <https://arxiv.org/abs/1602.07576>
- Steerable CNNs: <https://arxiv.org/abs/1612.08498>
- Harmonic Networks with circular harmonics: <https://arxiv.org/abs/1612.04642>
- General E(2)-equivariant steerable CNNs:
  <https://arxiv.org/abs/1911.08251>
- LieConv for Lie-group equivariance: <https://arxiv.org/abs/2002.12880>
- Spherical CNNs and generalized FFT: <https://arxiv.org/abs/1801.10130>
- Tensor Field Networks and spherical harmonics:
  <https://arxiv.org/abs/1802.08219>

Add:

- Lean: finite `C_n` equivariance first, then abstract group-equivariance
  contracts. Avoid full continuous Lie groups until the finite API is solid.
- Python: `circle_math.equivariance` with cyclic shift actions, feature-field
  type descriptors, equivariance test fixtures.
- Contracts: `cyclic_equivariance_contract`,
  `dihedral_equivariance_contract`, `harmonic_filter_rotation_contract`.

First small Lean targets:

- equivariant map composition is equivariant;
- convolution with circular kernel commutes with cyclic shifts;
- pooling over a finite orbit is rotation invariant;
- dihedral reflection action squares to identity and normalizes rotations.

### 6. Fourier Features, Periodic Activations, And Neural Operators

Why it belongs: Fourier features and sinusoidal activations are circle maps from
inputs into phases. Fourier neural operators learn in spectral/circular modes.

Sources:

- Fourier features for high-frequency learning:
  <https://arxiv.org/abs/2006.10739>
- SIREN periodic activations: <https://arxiv.org/abs/2006.09661>
- Fourier Neural Operator: <https://arxiv.org/abs/2010.08895>

Add:

- Python: Fourier feature maps with seeded random matrices and reproducible
  bandwidth metadata.
- Lean: simple periodicity/invariance facts for deterministic feature maps.
- Contracts: `fourier_feature_frequency_contract`,
  `periodic_activation_range_contract`, `spectral_mode_truncation_contract`.

First small Lean targets:

- sine/cosine feature pair has unit norm under exact real assumptions;
- feature map is periodic by declared period;
- truncating spectral modes is monotone on mode-set inclusion.

## Priority 2: Geometry, Topology, And Physics Tracks

### 7. Circle Packings And Discrete Conformal Geometry

Why it belongs: circle packings connect planar graphs, tangency, conformal maps,
and discrete complex analysis. This is a major circle-centered mathematical
world, but it is proof-expensive.

Sources:

- Koebe-Andreev-Thurston flow proof / algorithmic angle-overlap extension:
  <https://arxiv.org/abs/2007.02403>
- Packing disks by flipping and flowing:
  <https://arxiv.org/pdf/1910.02327>
- Decorated discrete conformal maps:
  <https://arxiv.org/abs/2305.10988>
- Inversive distance circle packing convergence:
  <https://arxiv.org/pdf/2204.08145>
- Local rigidity of inversive distance circle packing:
  <https://arxiv.org/abs/0903.1401>

Add:

- Start with executable data structures and elementary Lean lemmas, not full
  KAT theorem.
- Lean: tangency graph definitions, symmetric tangency, disjoint interiors for
  simple algebraic circles, Descartes-circle algebra as a separate reachable
  milestone.
- Python: circle packing graph schema, tangency validator, inversive-distance
  calculator.
- Contracts: `circle_tangency_graph_contract`,
  `inversive_distance_contract`, `packing_overlap_certificate`.

First small Lean targets:

- tangency relation is symmetric;
- disjoint interiors imply no crossing overlap;
- graph edge count in a finite tangency graph equals half the directed
  incidence count;
- Descartes curvature formula executable check for four mutually tangent
  circles.

### 8. Winding, Holonomy, Vortices, And Phase Oscillators

Why it belongs: winding number is the integer that records how a phase wraps
around a circle. Vortices, Kuramoto oscillators, and Aharonov-Bohm phase are all
circle-valued phase systems.

Sources:

- Mathlib circle topology foundation: <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Complex/Circle.html>
- Kuramoto review: <https://link.aps.org/doi/10.1103/RevModPhys.77.137>
- Stable phase-locked states and winding numbers on cycle networks:
  <https://arxiv.org/abs/1512.04266>
- Quantized vortices review: <https://arxiv.org/abs/1004.5458>
- Aharonov-Bohm phase/winding connection overview:
  <https://arxiv.org/abs/2601.17659>

Add:

- Lean: finite discrete winding over cyclic paths; loop-current integer for a
  cycle graph; phase difference sum around a cycle is an integer multiple of a
  full turn under closure.
- Python: Kuramoto cycle fixtures, winding-number calculators, phase-lock
  residual checks.
- Contracts: `cycle_phase_lock_winding_contract`,
  `vortex_charge_grid_contract`, `holonomy_phase_contract`.

First small Lean targets:

- discrete winding is additive under path concatenation;
- reversing a loop negates winding;
- constant loop has zero winding;
- cycle phase increments summing to one full turn have winding one.

### 9. Classical Euclidean Circle Geometry And Inversion

Why it belongs: chord, tangent, secant, cyclic quadrilateral, and inversion
theorems are the human-facing circle geometry canon. They also make the project
more approachable.

Sources:

- Mathlib Euclidean geometry basics:
  <https://leanprover-community.github.io/mathlib4_docs/Mathlib/Geometry/Euclidean/Basic.html>
- LeanEuclid/autoformalizing Euclidean geometry:
  <https://arxiv.org/abs/2405.17216>
- LeanGeo geometry theorem library:
  <https://arxiv.org/html/2508.14644v1>

Add:

- Lean: begin analytically over points in `R^2` or complex numbers; avoid
  diagram-heavy synthetic geometry at first.
- Python: exact rational-coordinate fixtures for chord/tangent/power-of-point.
- Docs: "Circle Theorem Gallery" with claim-boundary badges.

First small Lean targets:

- radius to tangent is perpendicular for an algebraic tangent line;
- equal chords at equal distance from center have equal length;
- perpendicular from center to chord bisects chord;
- power-of-point algebra for a coordinate circle.

### 10. Torus, Products Of Circles, And Multiphase Systems

Why it belongs: many AI and physics systems use many simultaneous phases. The
right object is not one circle but `S1^n`, a torus.

Sources:

- Mathlib overview for topology/groups: <https://leanprover-community.github.io/mathlib-overview.html>
- Directional statistics on higher spheres/tori via Mardia/Jupp:
  <https://books.google.com/books/about/Directional_Statistics.html?id=zjPvAAAAMAAJ>
- Multivariate von Mises circular models:
  <https://arxiv.org/html/2412.02333v1>

Add:

- Lean: finite torus as product of `ZMod` circles; coordinate projections;
  componentwise winding/period facts.
- Python: phase-vector utilities, torus distance, product-period/lcm helpers.
- Contracts: `multiphase_period_lcm_contract`,
  `torus_aliasing_contract`.

First small Lean targets:

- product period divides lcm of coordinate periods;
- coordinate projection preserves rotation action;
- componentwise zero phase iff all coordinates are zero.

## Priority 3: Library And Knowledge-Source Improvements

### 11. Circle Knowledge Map

Add a Living Book page that makes the project navigable by "circle role":

- finite circle / cyclic group;
- geometric circle / Euclidean object;
- unit complex circle / phase;
- circle action / rotation group;
- circle-valued random variable;
- circle graph / cyclic attention;
- circle packing / tangency;
- winding / topological charge;
- torus / product of circles.

Each node should link to Lean modules, Python APIs, papers, docs, and contracts.

### 12. Claim-Boundary Matrix For Research Tracks

For every new track, record:

- proved Lean facts;
- executable fixtures;
- empirical/numerical experiments;
- speculative ideas;
- non-claims.

This is especially important for AI topics where papers make empirical claims
that this repository should not repeat as proved mathematics.

## Recommended Implementation Order

1. Finite Fourier/circulant algebra.
2. General phase-bank positional encoding contracts.
3. Sparse-attention graph reachability/diameter contracts.
4. Circle-valued statistics.
5. Finite cyclic equivariance.
6. Winding/Kuramoto cycle contracts.
7. Euclidean circle theorem gallery.
8. Circle packing executable schemas.
9. Continuous/topological `S1` bridges using mathlib.
10. Torus/multiphase systems.

The fastest high-value next sprint is items 1-3. They directly improve the
project as a library, strengthen existing AI contracts, and keep proofs finite
and tractable.
