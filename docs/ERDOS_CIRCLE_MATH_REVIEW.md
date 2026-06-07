# Erdős Problem Review For Circle Calculus

Date: 2026-06-07

## Executive Finding

Circle Calculus is currently strongest as a finite cyclic-address formalization:
`Circle.C n` is `ZMod n`, with proved infrastructure for rotations, periods,
gcd orbit classes, scaling, fibers, kernels, and lifted winding. That makes the
best Erdős-facing target additive combinatorics in cyclic groups, not Euclidean
circle geometry.

The strongest immediate bridge is the Erdős-Ginzburg-Ziv theorem (EGZ): every
family of at least `2*n - 1` elements of `ZMod n` contains `n` elements summing
to zero. This is a recognized Erdős theorem, mathlib already has a formal proof,
and Circle Calculus can state it natively as a theorem about `C n`.

This review adds that bridge as:

- theorem id: `CC-T0062`
- Lean declaration: `Circle.erdos_ginzburg_ziv`
- source: `Circle/Erdos/EGZ.lean`

This is not a claim of a new proof. It is a rigorous external theorem contact
point: Circle's basic object is exactly the object in a nontrivial Erdős theorem.

## Current Project Fit

High-confidence fit:

- Finite cyclic groups and residues: already core.
- Additive zero-sum questions: direct match after adding sequence/multiset
  vocabulary.
- Sumset lower bounds on `ZMod p`: natural next bridge through Cauchy-Davenport.
- Computational witness/provenance tooling: consistent with the existing
  proof-carrying glyph and theorem-search lanes.

Weak or not-yet fit:

- Euclidean unit-distance and distinct-distance problems: Circle currently has
  finite address spaces, not Euclidean incidence geometry or algebraic number
  field norm constructions.
- Ramsey/Erdős-Hajnal/sunflower graph-set systems: possible formalization
  targets, but not specifically helped by the current circle-specific core.
- Deep analytic/density statements: Circle needs asymptotic density,
  representation functions, and transfer from finite cyclic models to `Nat`
  before these become serious.

## Erdős Landscape Checked

The live Erdős Problems database reports 1217 problems, 551 solved, and recent
status changes through June 2026:

- https://www.erdosproblems.com/

Thomas Bloom's April 2026 "Top 10 Erdős Problems" is a useful triage list for
high-value targets:

- https://www.erdosproblems.com/forum/thread/blog%3A5

Notable status-sensitive items checked:

- Unit distances, problem #90: now marked disproved after the May 2026 OpenAI
  construction; this is geometry/number-field heavy and not a good immediate
  Circle target. Source: https://www.erdosproblems.com/90
- Arithmetic progressions from divergent reciprocal sum sets, problem #3:
  open and central, but needs density/additive-combinatorics machinery beyond
  the current finite-circle core. Source: https://www.erdosproblems.com/3
- Erdős-Turán additive basis conjecture, problem #28: open; medium long-term
  fit because it is about additive representation functions. Source:
  https://www.erdosproblems.com/28
- Sum-product, problem #52: open; currently low-medium fit because Circle has
  modular scaling but not a real integer sum-product engine. Source:
  https://www.erdosproblems.com/52
- Erdős discrepancy, problem #67: solved by Tao; finite homogeneous arithmetic
  progression fixtures could be Circle-friendly, but the proof uses much deeper
  multiplicative-function theory. Source: https://www.erdosproblems.com/67
- Erdős-Straus, problem #242: open and modular-search friendly, but a Circle
  contribution would likely be a residue/provenance sieve unless new number
  theory is added. Source: https://www.erdosproblems.com/242

## Target Ranking

1. Best rigorous solved-theorem target: Erdős-Ginzburg-Ziv.
   EGZ is directly about zero sums in `ZMod n`, and mathlib exposes
   `ZMod.erdos_ginzburg_ziv`. Circle now wraps it as `CC-T0062`.

2. Best next formal bridge: Cauchy-Davenport on `ZMod p`.
   This is not itself an Erdős problem, but it is core additive combinatorics and
   a standard route into zero-sum results. Mathlib has `ZMod.cauchy_davenport`.
   A Circle wrapper would give the project a sumset API.

3. Best hard solved Erdős problem for explanatory fixtures: Erdős discrepancy.
   Homogeneous arithmetic progressions look like finite coils. The honest target
   would be finite discrepancy definitions, bounded examples, SAT/property-test
   fixtures, and clear explanation of why this does not reproduce Tao's proof.

4. Best open long-horizon target: Erdős-Turán additive bases (#28).
   This is the most plausible open problem for Circle influence because it is
   about additive representation counts. Circle would need new formal layers:
   finite sumsets, representation functions, density/asymptotic transfer, and
   probably Kneser/Cauchy-Davenport style theorem bridges.

5. Best computational open target: Erdős-Straus (#242).
   Circle's residue/fiber/provenance machinery may produce a clean modular
   certificate or search interface. That would be useful, but it should not be
   advertised as a likely route to a proof without a genuinely new reduction.

## What Would Count As Community-Rigorous

A credible Circle-Erdős program should proceed in this order:

1. Publish a short "EGZ as a zero-sum circle theorem" paper in the repo.
   It should cite the original theorem and mathlib, state that the proof is
   imported/wrapped rather than new, and explain why `C n = ZMod n` is a natural
   Circle object for the theorem.

2. Add the sharpness example for EGZ.
   The sequence with `n-1` zeros and `n-1` ones in `C n` has length `2*n-2`
   and no zero-sum subsequence of length `n`. This would show Circle can explain
   both the theorem and the tight threshold.

3. Add `Circle.cauchy_davenport_prime`.
   This would connect Circle's finite-address language to sumset growth, the
   standard engine behind many additive-combinatorics arguments.

4. Build zero-sum witness tooling.
   Define finite address families, zero-sum subsequences, witness certificates,
   and small deterministic search examples. Keep Python as executable support,
   not proof.

5. Only then attempt an open Erdős problem lane.
   For #28, start with finite cyclic representation functions and known finite
   lower bounds. For #242, start with modular residue-class certificates. In
   both cases, record all results as partial, computational, or exploratory
   until they have a theorem statement and proof.

## Claim Boundary

Circle Calculus is not currently novel enough to credibly claim progress on a
major open Erdős problem. It is novel enough to become a rigorous proof-carrying
interface for cyclic additive-combinatorics theorems, beginning with EGZ. That
is the right first public mathematical claim: small, checkable, externally
recognized, and aligned with the formal core.

## Source Pointers

- Circle formal core: `docs/FORMAL_CORE_V0.md`
- Circle proof policy: `docs/PROOF_POLICY.md`
- EGZ bridge: `Circle/Erdos/EGZ.lean`
- Theorem registry entry: `CC-T0062` in `manifests/theorem_manifest.yaml`
- mathlib EGZ documentation:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Combinatorics/Additive/ErdosGinzburgZiv.html
- mathlib Cauchy-Davenport documentation:
  https://leanprover-community.github.io/mathlib4_docs/Mathlib/Combinatorics/Additive/CauchyDavenport.html
