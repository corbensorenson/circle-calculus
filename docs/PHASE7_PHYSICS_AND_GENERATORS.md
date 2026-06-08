# Phase VII: Physics And Generative Structure

Phase VII adds two tightly related research tracks after the global sweep:

- physics-facing Circle Calculus, where phase, gauge, fiber, holonomy, spin, winding, and periodic dynamics are already native mathematical objects;
- generative structure, where an object is represented by the smallest honest seed plus rules that regenerate it, with provenance and proof status attached to every rule.

This phase is not a claim that Circle Calculus replaces standard physics, gauge theory, topology, compression theory, or algorithmic information theory. The underlying mathematics is mostly standard. The possible contribution is a proof-carrying interface that keeps visible state, hidden phase, rules, generation history, theorem ids, and executable checks linked.

## Source Of Truth

The active target manifest is:

```text
manifests/phase7_physics_generators.yaml
```

It is validated by:

```text
python scripts/check_phase7_targets.py
```

Target status is weaker than theorem status. A Phase VII target becomes a proved theorem only after it has a theorem id, a compiled Lean declaration, manifest status, and passing proof checks.

## Physics Program

The first physics slice is now `PAPER_PHYS_01_PROOF_CARRYING_LATTICE_GAUGE`, a proof-carrying finite `U(1)`-style or `Z_n` lattice gauge model with Lean-proved `ZMod n` phase-list and link-path record theorems plus Python graph fixtures.

Start with a finite graph:

```text
vertex gauge choices
edge link phases
path holonomy
closed Wilson loops
plaquette loops
```

The first theorem spine is finite and auditable:

```text
pathHolonomy_concat
pathHolonomy_reverse
gaugeLinkPathHolonomy_concat
gaugeLinkPathHolonomy_reverse
gaugeLinkPath_singleton_composable
gaugeLinkPath_pair_composable_iff
gaugeLinkPath_concat_singletons_composable_iff
gaugeLinkPath_triple_composable_iff
gaugeLinkPath_quad_composable_iff
gaugeLinkPath_empty_composable
gaugeLinkPath_concat_empty_left_composable
gaugeLinkPath_concat_empty_right_composable
gaugeLinkPath_concat_empty_left
gaugeLinkPath_concat_empty_right
gaugeLinkPath_concat_assoc
gaugeLink_reverse_reverse
gaugeLinkPath_reverse_reverse
gaugeLinkPath_reverse_concat
linksComposable_append_of_composable
gaugeLinkPath_concat_composable_of_boundary
gaugeLinkPath_source?_concat_cons_left
gaugeLinkPath_target?_concat_cons_right
linksBoundaryComposable_of_endpoints
linksHaveEndpoints_append
checkedGaugePath_identity_source
checkedGaugePath_identity_target
checkedGaugePath_singleton_source
checkedGaugePath_singleton_target
checkedGaugePath_concat_source
checkedGaugePath_concat_target
checkedGaugePath_concat_identity_left
checkedGaugePath_concat_identity_right
checkedGaugePath_concat_assoc
checkedGaugePath_identity_holonomy
checkedGaugePath_singleton_holonomy
checkedGaugePath_concat_holonomy
checkedGaugePath_toLinkPath_composable
checkedGaugePath_toLinkPath_holonomy
checkedGaugePath_toLinkPath_concat
checkedGaugePath_identity_closed
checkedGaugePath_concat_closed_of_cycle
checkedGaugePath_closed_gaugeInvariant
gaugeTransform_pathHolonomy_endpoints
closedWilsonLoop_gaugeInvariant
plaquetteHolonomy_gaugeInvariant
```

This is a good Circle Calculus target because a loop diagram can become:

```text
glyph -> finite path object -> theorem id -> Lean declaration -> paper section -> Living Book widget
```

The finite-gauge seed now includes singleton/two-link/singleton-concat/three-link/four-link/empty-identity, record-associativity, reversal-algebra, general boundary-checked append composability, first source/target laws for nonempty concatenations, and a checked finite path interface with explicit endpoints, identity laws, associative boundary-checked composition, checked-path holonomy identity/singleton/concat laws, projection bridges back to the link-path carrier, and closed checked-path gauge-invariance facts. The Living Book now exposes finite path algebra, plaquette holonomy, Wilson-loop certificate, and quaternion spin sign ambiguity widgets with theorem/dictionary links. The next finite-gauge step is to decide whether a full finite graph path-category instance is worth the abstraction:

- Berry/geometric phase and Aharonov-Bohm-style holonomy primers;
- Hopf/Bloch-sphere hidden phase lessons linked to the existing `S3` Hopf spine;
- deeper quaternion quotient lessons beyond the current bounded `q/-q` sign widget;
- Floquet and action-angle periodic dynamics using winding, residue, and lift vocabulary;
- vortex and topological-defect winding examples with clear continuum guardrails;
- topological phase/Bott/Clifford connections as later background and target discovery, not first-pass claims.

## Generative Structure Program

The core idea is:

```text
do not merely compress the finished object;
find the smallest checked generator that can rebuild it.
```

A generator record should include:

```text
seed
rule set
iteration schedule
closure or stopping condition
generated object
provenance trace
dictionary ids
theorem ids
proof status
ordinary baseline description
```

The first concrete lane is finite and implemented in `PAPER_GEN_01_SEED_RULE_PROVENANCE`:

- regenerate finite circles, finite-circle diagrams, finite physics-loop diagrams, coils, orbit decompositions, and glyph diagrams from seed/rule records;
- compare value-only/object-only descriptions against seed-plus-rule descriptions;
- run bounded finite-list generator searches that report exact candidates and shorter exact candidates without claiming global minimality;
- report description length, regeneration exactness, proof coverage, and where the generator adds noise;
- never call a generator minimal unless the minimization criterion and search space are explicit.

The first Lean seed lives in `Circle.Generative.SeedRule`: finite-circle node regeneration, period-indexed coil-orbit schedule regeneration, representative-indexed orbit-decomposition schedule regeneration, orbit-count/period/coverage/orbit-class agreement facts, canonical representative coverage/disjointness facts, proof-glyph field regeneration, exact-regeneration comparison, exact-regeneration self/symmetry/transitivity facts, comparison field-equality gates, and unequal-value negative gates are checked there. The Python fixture also regenerates finite-circle and finite physics-loop diagrams from the same seed/rule/provenance contract, adds bounded finite-list generator search, and the Living Book now has a generated-diagram widget that exposes the corresponding seed, rules, theorem-status badges, and dictionary ids. Orbit-family/proof-glyph widget expansion and compression-minimality claims remain future work; minimality claims need an explicit search space before they can be formal targets.

This reframes compression as constructive provenance. The useful question is not only "how short is the encoding?" but:

```text
Can the object be rebuilt, audited, explained, and linked to proofs from the generator?
```

## Guardrails

- Physics claims remain model, proof-target, or benchmark claims until formalized.
- A finite gauge model is not full continuum QFT.
- A holonomy widget is not a proof of Berry phase, electromagnetism, or quantum mechanics.
- A generator description is not automatically minimal.
- A smaller seed is not automatically more meaningful.
- Python regeneration tests are executable evidence, not formal proofs.
- Lean can prove finite generation, closure, equality, and invariance facts; it does not by itself prove empirical physics usefulness or compression optimality.

## Living Book Role

The Living Book should teach Phase VII as guided lessons:

```text
finite gauge loops -> holonomy -> Hopf hidden phase -> spin sign ambiguity -> periodic dynamics -> winding defects -> minimal generators -> generator provenance -> proof-carrying generative diagrams
```

Each mature lesson should show the ordinary baseline, the Circle Calculus representation, the proof boundary, the executable fixture, and the limitation before source links.
