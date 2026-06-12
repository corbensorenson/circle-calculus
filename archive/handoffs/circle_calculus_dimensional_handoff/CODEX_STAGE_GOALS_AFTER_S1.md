# Codex Stage Goals After S¹

Use these as staged `/goal` prompts after the existing S¹ work completes.

## Stage D0 — Dimensional scaffolding only

```text
/goal Add dimension-organized scaffolding for the Circle Calculus dimensional ladder without changing proved S¹ mathematics.

Create dimension_index.yaml, dimension manifests, dictionary dimension files, paper directories, Lean directory scaffolding, Python exploratory directory scaffolding, and dimension check scripts. All S²/S³/S⁴/S⁵/S⁶/S⁷ theorem statuses must remain planned or deferred. Do not implement Manim. Do not mark future theorem proofs. Preserve S¹ green CI.

Run:
lake build
python -m pytest
python scripts/check_manifest.py
python scripts/check_dictionary.py
python scripts/check_dimension_index.py
python scripts/check_dimension_imports.py
python scripts/check_dimension_manifests.py
python scripts/check_dimension_paper_links.py
```

## Stage S2.1 — Suspended finite circles

```text
/goal Implement S² finite suspended-circle calculus.

Define SuspC(n) for n >= 3 as the suspension of C_n. Implement Lean count formulas and prove V=n+2, E=3n, F=2n, and χ=2. Add Python reference model and tests. Draft papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md with theorem ids linked to Lean names.

Do not introduce continuous Euclidean sphere geometry. Do not treat the drawing as proof.
```

## Stage S2.2 — Sphere grids and latitude coils

```text
/goal Implement S² sphere grids and latitude coil inheritance.

Define SphereGrid(n,r) for n>=3 and r>=1 with north/south pole collapse and r latitude rings. Prove V=nr+2, E=n(2r+1), F=n(r+1), and χ=2. Prove each latitude ring is C_n-like and its coil period is inherited from S¹: n/gcd(n,k). Add warnings/tests preventing C_n × C_m from being identified as a sphere.

Draft PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md.
```

## Stage S3.1 — Finite 3-spheres by suspension

```text
/goal Implement S³ finite hypersphere combinatorics.

Define suspension of a finite 2D cell-count model. Prove that if K has counts V,E,F, then Susp(K) has V'=V+2, E'=E+2V, F'=F+2E, T'=2F. Prove that if χ(K)=2 then χ(Susp(K))=0. Instantiate K=SuspC(n) and prove V=n+4, E=5n+4, F=8n, T=4n, χ=0.

Draft PAPER_S3_01_FINITE_HYPERSPHERES.md.
```

## Stage S3.2 — Quaternion calculus

```text
/goal Implement S³ quaternion calculus.

Check current mathlib support for quaternions. Prefer importing Mathlib.Algebra.Quaternion if available. Define unit quaternions as the S³ algebraic model. Prove or stage: norm behavior, conjugate inverse for units, closure of unit quaternions under multiplication, associativity, and a formal noncommutativity example i*j ≠ j*i.

Draft PAPER_S3_02_QUATERNION_COILS.md.

Do not attempt Hopf fibration before quaternion basics are green.
```

## Stage S3.3 — Hopf coils

```text
/goal Implement the S³ Hopf-coil roadmap and executable model.

Create Python model for the Hopf map h:S³→S² using complex pairs. Test numerically that h maps normalized S³ points to S² and that simultaneous S¹ phase rotation preserves h. Add Lean theorem statements only where support is ready; prove only what can be proved without sorry/admit/unapproved axioms.

Draft PAPER_S3_03_HOPF_COILS.md.

Hard rule: do not claim S³ is globally S²×S¹.
```

## Stage S456.1 — General suspension and Euler parity

```text
/goal Implement the S⁴-S⁶ geometric higher-sphere bridge.

Generalize the finite suspension-count model. Prove χ(Susp(K))=2-χ(K) and derive χ(S^d)=1+(-1)^d for iterated suspension models. Instantiate S4, S5, and S6 Euler characteristics. Draft PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md and roadmap papers for S4/S5/S6.

Do not overclaim special algebraic structure for S4-S6.
```

## Stage S7.1 — Topological S7

```text
/goal Implement topological S⁷ by iterated suspension.

Use the general suspension model to construct finite S7 and prove χ(S7)=0. Draft PAPER_S7_01_TOPOLOGICAL_7SPHERE.md.

Do not introduce octonions yet.
```

## Stage S7.2 — Quaternionic Hopf roadmap

```text
/goal Add the quaternionic Hopf fibration roadmap S³→S⁷→S⁴.

Create theorem manifest entries, dictionary entries, Python exploratory stubs, and paper draft PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md. Do not mark as proved unless formalized. Reuse S3 quaternion calculus and S4 finite/geometric base concepts.
```

## Stage S7.3 — Octonion exploratory algebra

```text
/goal Add exploratory S⁷ octonion calculus without claiming proved foundational status.

Check whether current mathlib has octonion support. If not, implement a minimal exploratory Python model and optionally a Lean experimental module outside the proved core. Add tests for multiplication table, conjugate, norm, noncommutativity, and nonassociativity examples.

Draft PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md.

Hard rules:
- unit octonions are not a group,
- bracketing matters,
- no octonion theorem is marked Lean-proved without robust no-axiom formalization.
```
