# Circle Calculus Physics 1: Proof-Carrying Finite Lattice Gauge Links

Status: draft with a Lean-proved finite `ZMod n` theorem spine and Python fixtures.

## Aim

This paper starts the physics-facing Circle Calculus lane with the smallest model that is useful and honest: finite phase labels on oriented graph edges. A path accumulates edge phases modulo a positive modulus. A vertex gauge choice shifts each incident edge phase. A closed path has no exposed endpoint, so the endpoint shifts cancel in the finite model.

The ordinary baseline is standard lattice gauge notation: link variables live on directed edges, paths multiply or add link phases, and a Wilson loop records the phase around a closed path. Circle Calculus does not replace that mathematics. The contribution here is an auditable interface:

```text
finite diagram
  -> edge/path record
  -> path holonomy
  -> gauge transform certificate
  -> theorem id and dictionary ids
  -> Python example and Lean target
```

This first slice uses additive `Z_n` phases. That is a finite `U(1)`-style toy, not continuum electromagnetism, quantum field theory, Yang-Mills theory, or a physics prediction.

## Source Trail

The sidecar registered in the paper manifest is:

```text
sidecars/PAPER_PHYS_01_PROOF_CARRYING_LATTICE_GAUGE
```

The Lean sidecar is:

```text
sidecars/PAPER_PHYS_01_PROOF_CARRYING_LATTICE_GAUGE/lean/PaperPhys01.lean
```

The Python examples are:

```text
sidecars/PAPER_PHYS_01_PROOF_CARRYING_LATTICE_GAUGE/python/test_lattice_gauge_examples.py
```

The proof status boundary is strict: Lean declarations determine formal theorem status. Python examples check finite executable behavior and provide regression fixtures; they are not formal proofs or physics evidence.

## Dictionary Vocabulary

- `COMMON-0060`: finite gauge link.
- `COMMON-0061`: path holonomy.
- `COMMON-0062`: Wilson loop certificate.
- `COMMON-0063`: phase holonomy warning.

The paper also connects backward to bundle vocabulary in `PAPER_P2_03_BUNDLE_CALCULUS`, Hopf phase fibers in `PAPER_S3_03_HOPF_COILS`, spin sign ambiguity in `PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP`, and winding in the S1 winding lane.

## Theorem Spine

- `PHYS-T0001`: `Circle.Physics.pathHolonomy_concat`, finite path holonomy is additive under path concatenation.
- `PHYS-T0002`: `Circle.Physics.pathHolonomy_reverse`, reversing a path negates its finite holonomy.
- `PHYS-T0003`: `Circle.Physics.gaugeTransform_pathHolonomy_endpoints`, a gauge-transformed path holonomy changes only by endpoint gauge values.
- `PHYS-T0004`: `Circle.Physics.closedWilsonLoop_gaugeInvariant`, a closed Wilson loop is invariant under finite vertex gauge transforms.
- `PHYS-T0005`: `Circle.Physics.plaquetteHolonomy_gaugeInvariant`, a finite square plaquette loop has gauge-invariant holonomy.
- `PHYS-T0006`: `Circle.Physics.gaugeLinkPathHolonomy_concat`, finite link-path record holonomy is additive under path-record concatenation.
- `PHYS-T0007`: `Circle.Physics.gaugeLinkPathHolonomy_reverse`, reversing a finite link-path record negates its holonomy.
- `PHYS-T0008`: `Circle.Physics.gaugeLinkPath_singleton_composable`, a one-link finite gauge-link path record is compositionally valid.
- `PHYS-T0009`: `Circle.Physics.gaugeLinkPath_pair_composable_iff`, a two-link finite gauge-link path record is composable exactly when the first target is the second source.
- `PHYS-T0010`: `Circle.Physics.gaugeLinkPath_concat_singletons_composable_iff`, concatenating two one-link finite gauge-link path records is composable exactly when the boundary target/source matches.
- `PHYS-T0011`: `Circle.Physics.gaugeLinkPath_triple_composable_iff`, a three-link finite gauge-link path record is composable exactly when both adjacent source-target boundaries match.
- `PHYS-T0012`: `Circle.Physics.gaugeLinkPath_quad_composable_iff`, a four-link finite gauge-link path record is composable exactly when all three adjacent source-target boundaries match.
- `PHYS-T0013`: `Circle.Physics.gaugeLinkPath_empty_composable`, the empty finite gauge-link path record is compositionally valid.
- `PHYS-T0014`: `Circle.Physics.gaugeLinkPath_concat_empty_left_composable`, left-concatenating the empty finite gauge-link path record preserves composability.
- `PHYS-T0015`: `Circle.Physics.gaugeLinkPath_concat_empty_right_composable`, right-concatenating the empty finite gauge-link path record preserves composability.
- `PHYS-T0016`: `Circle.Physics.gaugeLinkPath_concat_empty_left`, left-concatenating the empty finite gauge-link path record returns the original path record.
- `PHYS-T0017`: `Circle.Physics.gaugeLinkPath_concat_empty_right`, right-concatenating the empty finite gauge-link path record returns the original path record.
- `PHYS-T0018`: `Circle.Physics.gaugeLinkPath_concat_assoc`, finite gauge-link path-record concatenation is associative.
- `PHYS-T0019`: `Circle.Physics.gaugeLink_reverse_reverse`, reversing a finite gauge link twice returns the original link record.
- `PHYS-T0020`: `Circle.Physics.gaugeLinkPath_reverse_reverse`, reversing a finite gauge-link path record twice returns the original path record.
- `PHYS-T0021`: `Circle.Physics.gaugeLinkPath_reverse_concat`, reversing a concatenated finite gauge-link path record equals concatenating the reversed right path before the reversed left path.
- `PHYS-T0022`: `Circle.Physics.linksComposable_append_of_composable`, two composable finite gauge-link lists append to a composable list when their boundary target/source matches.
- `PHYS-T0023`: `Circle.Physics.gaugeLinkPath_concat_composable_of_boundary`, two finite gauge-link path records concatenate to a composable path record when each side is composable and their boundary matches.
- `PHYS-T0024`: `Circle.Physics.gaugeLinkPath_sourceOpt_concat_cons_left`, concatenating with a nonempty left path keeps the leftmost source.
- `PHYS-T0025`: `Circle.Physics.gaugeLinkPath_targetOpt_concat_cons_right`, concatenating with a nonempty right path keeps the right path target.
- `PHYS-T0026`: `Circle.Physics.linksBoundaryComposable_of_endpoints`, endpoint records imply boundary composability for finite gauge-link lists.
- `PHYS-T0027`: `Circle.Physics.linksHaveEndpoints_append`, appending endpoint-checked finite gauge-link lists preserves source and target endpoints.
- `PHYS-T0028`: `Circle.Physics.checkedGaugePath_identity_source`, a checked identity path has source equal to its vertex.
- `PHYS-T0029`: `Circle.Physics.checkedGaugePath_identity_target`, a checked identity path has target equal to its vertex.
- `PHYS-T0030`: `Circle.Physics.checkedGaugePath_singleton_source`, a checked singleton path has source equal to its link source.
- `PHYS-T0031`: `Circle.Physics.checkedGaugePath_singleton_target`, a checked singleton path has target equal to its link target.
- `PHYS-T0032`: `Circle.Physics.checkedGaugePath_concat_source`, checked path concatenation keeps the left source.
- `PHYS-T0033`: `Circle.Physics.checkedGaugePath_concat_target`, checked path concatenation keeps the right target.
- `PHYS-T0034`: `Circle.Physics.checkedGaugePath_concat_identity_left`, left-concatenating a checked identity path returns the checked path.
- `PHYS-T0035`: `Circle.Physics.checkedGaugePath_concat_identity_right`, right-concatenating a checked identity path returns the checked path.
- `PHYS-T0036`: `Circle.Physics.checkedGaugePath_concat_assoc`, checked finite gauge path concatenation is associative when the source-target boundaries match.
- `PHYS-T0037`: `Circle.Physics.checkedGaugePath_identity_holonomy`, a checked identity path has zero holonomy.
- `PHYS-T0038`: `Circle.Physics.checkedGaugePath_singleton_holonomy`, a checked singleton path has holonomy equal to the link phase.
- `PHYS-T0039`: `Circle.Physics.checkedGaugePath_concat_holonomy`, checked path holonomy is additive under boundary-checked concatenation.
- `PHYS-T0040`: `Circle.Physics.checkedGaugePath_toLinkPath_composable`, projecting a checked path to its link-path carrier preserves composability.
- `PHYS-T0041`: `Circle.Physics.checkedGaugePath_toLinkPath_holonomy`, projecting a checked path to its link-path carrier preserves holonomy.
- `PHYS-T0042`: `Circle.Physics.checkedGaugePath_toLinkPath_concat`, projecting a checked concatenation matches concatenating the projected link-path carriers.
- `PHYS-T0043`: `Circle.Physics.checkedGaugePath_identity_closed`, a checked identity path is closed.
- `PHYS-T0044`: `Circle.Physics.checkedGaugePath_concat_closed_of_cycle`, two checked paths form a closed loop when their endpoints cycle back.
- `PHYS-T0045`: `Circle.Physics.checkedGaugePath_closed_gaugeInvariant`, a closed checked path has gauge-shifted holonomy equal to its original holonomy because endpoint shifts cancel.
- `PHYS-T0046`: `Circle.Physics.checkedGaugePath_concat_cycle_gaugeInvariant`, two checked paths whose endpoints cycle back have gauge-invariant concatenated holonomy.
- `PHYS-T0047`: `Circle.Physics.closedGaugeLoop_gaugeInvariant`, a closed finite gauge-loop record has gauge-shifted holonomy equal to its original holonomy.
- `PHYS-T0048`: `Circle.Physics.closedGaugeLoop_identity_holonomy`, the checked finite identity loop has zero holonomy.
- `PHYS-T0049`: `Circle.Physics.closedGaugeLoop_fromCycle_holonomy`, a closed finite two-path cycle has holonomy equal to the sum of the two checked path holonomies.
- `PHYS-T0050`: `Circle.Physics.gaugeLinkPath_concat_reverse_holonomy`, a finite gauge-link path followed by its reversed path has zero holonomy.
- `PHYS-T0051`: `Circle.Physics.gaugeLinkPath_reverse_concat_holonomy`, a reversed finite gauge-link path followed by the original path has zero holonomy.
- `PHYS-T0052`: `Circle.Physics.closedGaugeLoop_identity_gaugeShiftedHolonomy`, the checked finite identity loop has zero gauge-shifted holonomy under any finite vertex gauge.
- `PHYS-T0053`: `Circle.Physics.closedGaugeLoop_fromCycle_gaugeShiftedHolonomy`, a closed finite two-path cycle has gauge-shifted holonomy equal to the sum of the two checked path holonomies.
- `PHYS-T0054`: `Circle.Physics.closedGaugeLoop_fromCycle_swap_holonomy`, swapping the basepoint order of a finite two-path closed cycle preserves packaged loop holonomy.
- `PHYS-T0055`: `Circle.Physics.closedGaugeLoop_fromCycle_swap_gaugeShiftedHolonomy`, swapping the basepoint order of a finite two-path closed cycle preserves sampled gauge-shifted holonomy.
- `PHYS-T0056`: `Circle.Physics.closedGaugeLoop_fromThreeCycle_holonomy`, a closed finite three-path cycle has holonomy equal to the sum of the three checked path holonomies.
- `PHYS-T0057`: `Circle.Physics.closedGaugeLoop_fromThreeCycle_gaugeShiftedHolonomy`, a closed finite three-path cycle has gauge-shifted holonomy equal to the sum of the three checked path holonomies.
- `PHYS-T0058`: `Circle.Physics.closedGaugeLoop_fromThreeCycle_rotate_holonomy`, rotating the basepoint order of a finite three-path closed cycle preserves packaged loop holonomy.
- `PHYS-T0059`: `Circle.Physics.closedGaugeLoop_fromThreeCycle_rotate_gaugeShiftedHolonomy`, rotating the basepoint order of a finite three-path closed cycle preserves sampled gauge-shifted holonomy.

These theorem ids are Lean-proved in `Circle.Physics.LatticeGauge` for the finite `ZMod n` phase model. `PHYS-T0006` through `PHYS-T0059` move from bare phase lists toward finite link/path records, source-target composability, singleton concatenation, three-/four-link source-target laws, empty-path identity-style composability laws, record-level identity/associativity laws for concatenation, record-level reversal laws, path-plus-reverse zero-holonomy gates, general boundary-checked append composability, first source/target laws for nonempty concatenations, a checked finite path interface with explicit endpoints, identities, associative boundary-checked composition, checked-path holonomy identity/singleton/concat laws, projection bridges back to the link-path carrier, closed checked-path gauge-invariance facts, a packaged two-path cycle gauge-invariance certificate, and a reusable closed-loop record with identity/cycle holonomy, gauge-shifted holonomy, two-path basepoint-swap facts, and three-path basepoint-rotation facts. They do not yet install a full mathlib category instance for finite graph paths. They do not prove continuum gauge theory.

## Finite Model

Fix a positive modulus `n`. A finite gauge link is an oriented edge:

```text
source -- phase mod n --> target
```

A path is a composable sequence of links. Its holonomy is:

```text
holonomy(path) = sum(edge.phase for edge in path) mod n
```

Concatenating two composable paths adds their holonomies modulo `n`. Reversing a path reverses edge order and negates each phase modulo `n`.

The Lean model now has a bounded `GaugeLink`/`GaugeLinkPath` record layer:

```text
GaugeLink(source,target,phase)
GaugeLinkPath([links]).holonomy = sum(link.phase)
```

The first record-level theorems prove that link-path holonomy respects record concatenation and reversal. This is still finite algebraic bookkeeping: the Python fixture enforces path composability at runtime, while the current Lean record theorem treats the link list as the audited phase carrier.

The next composability and reversal seeds are also in Lean: one-link paths are composable, a two-link path is composable exactly when the first link's target is the second link's source, concatenating singleton paths has the same boundary condition, a three-link path is composable exactly when both adjacent boundaries match, a four-link path is composable exactly when all three adjacent boundaries match, and the empty link path acts as a left/right identity for both the composability predicate and the path-record concatenation operation. Finite path-record concatenation is associative. Reversal is involutive on links and path records, and reversal turns concatenation around. A general boundary predicate now proves that appending two composable finite link paths remains composable when the left target and right source match, and the first nonempty source/target projection laws are checked for concatenation.

The checked path interface packages this into an explicit finite record:

```text
CheckedGaugePath(source, target, links, composable, endpoints)
```

It has an identity path at a vertex, singleton paths from links, boundary-checked composition, source/target laws for identity, singleton, and concatenated paths, left/right identity laws, an associativity law for boundary-checked composition, holonomy laws for identity, singleton, and boundary-checked concatenation, and projection lemmas showing that a checked path's link carrier is composable, preserves holonomy, and respects concatenation. This is a category-style interface seed, not a completed category instance for all finite graph paths.

A vertex gauge is a function:

```text
g : vertices -> Z_n
```

The transformed phase of an edge `u -> v` is:

```text
g(u) + phase(u,v) - g(v) mod n
```

For an open path from `s` to `t`, all interior vertex shifts cancel, leaving:

```text
holonomy(gauge(path)) =
  holonomy(path) + g(s) - g(t) mod n
```

For a closed path, `s = t`, so the endpoint term is zero.

## Executable Fixture

The Python fixture implements:

```text
GaugeEdge
GaugePath
path_holonomy
concat_paths
reverse_path
gauge_transform_path
transformed_holonomy_endpoint_prediction
square_plaquette_path
wilson_loop_certificate
closed_loop_record
identity_closed_loop_record
cycle_closed_loop_record
```

The tests cover concatenation, reversal, open-path endpoint behavior, closed Wilson-loop invariance, identity/cycle closed-loop records, open-path rejection for closed-loop records, and a square plaquette. The fixture deliberately reports a finite certificate, not a continuum field strength.

## Circle Calculus Framing

The Circle Calculus vocabulary is useful here because the same finite phase discipline used for circles, winding, and Hopf fibers also describes gauge-link bookkeeping:

```text
circle phase      -> edge phase
coil/path         -> composed route
closure           -> closed loop
winding residue   -> finite holonomy
fiber shift       -> gauge choice
certificate       -> source-linked proof object
```

That framing is useful only if the source trail stays attached. A visual loop or generated diagram is an explanation. The formal status lives in the theorem manifest and Lean source.

## Limits

This paper does not model a continuum manifold, a differentiable connection, curvature forms, electric or magnetic fields, Berry phase, QED, QCD, Yang-Mills theory, lattice simulation, or experimental physics. It is a finite proof-carrying interface for gauge-link bookkeeping.

The next formal step is to decide whether a full finite graph path-category instance is useful enough to justify the extra abstraction, or whether the explicit `CheckedGaugePath` plus `ClosedGaugeLoop` interface is the clearer paper-facing artifact.
