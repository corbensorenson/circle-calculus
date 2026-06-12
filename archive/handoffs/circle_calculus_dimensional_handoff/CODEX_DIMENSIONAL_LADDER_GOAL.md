# Circle Calculus — Dimensional Ladder Continuation Goal

Paste this into Codex after the existing S¹ / finite circle core has reached a stable green state.

```text
/goal Extend the Circle Calculus repository with a dimension-organized long-horizon roadmap, proof/module scaffolding, dictionary extensions, theorem manifests, and paper organization for the post-S¹ dimensional ladder: S² sphere calculus, S³ hypersphere/quaternion/Hopf calculus, S⁴-S⁶ geometric higher-sphere bridge, and S⁷ octonionic/quaternionic-Hopf calculus.

Do not implement Manim, TTS, captions, or video systems in this goal.

Current project status:
- The active formal core is S¹ / finite circle calculus.
- S¹ uses finite cyclic address spaces C_n, rotations, coils, closure, period, and prime full-coil behavior.
- The S¹ core must remain clean, green, and lower-level.
- Higher-dimensional work may import lower-dimensional work, but lower-dimensional work must never import higher-dimensional work.

Primary outcome:
Create a repository structure and research roadmap where papers, Lean modules, Python prototypes, theorem manifests, and dictionary entries are organized by sphere dimension.

Core notation convention:
- Use topological sphere notation.
- S^0 = two-point sphere / sign opposition.
- S^1 = circle.
- S^2 = ordinary sphere surface.
- S^3 = 3-sphere / 4D hypersphere / unit quaternions.
- S^7 = 7-sphere / unit octonions.
- C_n is the finite cyclic address-space model used for S¹ finite core.
- C_1, the one-node point-circle, is not the same thing as S^0.

Hard constraints:
1. Do not modify S¹ theorem statuses unless S¹ proofs are actually changed and lake build is green.
2. Do not move existing S¹ files until the current S¹ goal is complete.
3. If refactoring S¹ into a new dimension-organized layout, preserve backwards-compatible import shims.
4. Do not mark any S²/S³/S⁴/S⁵/S⁶/S⁷ theorem as Lean-proved unless it has a compiled Lean theorem with no sorry/admit/unapproved axiom/unsafe.
5. Python tests are exploratory checks and executable examples, not formal proofs.
6. Continuous geometry, real analysis, smooth manifolds, Hopf fibrations, quaternions, and octonions must be staged after finite combinatorial versions.
7. Do not claim S² has a natural group structure.
8. Do not claim S³ is globally S² × S¹.
9. Do not claim unit octonions form a group. They are nonassociative; eventual algebraic structure should be treated as a Moufang-loop-like target unless formally proven otherwise.
10. Do not use projections, slices, or pictures as proofs.
11. Do not treat C_n × C_m as a sphere; that is torus-like behavior, not sphere behavior.
12. Do not rely on unresolved claims about S^6 complex structures. Mark those topics as warning/speculative unless formalized from accepted sources.

Required repository additions:
1. Add a dimension index:
   - manifests/dimensions/dimension_index.yaml

2. Add dimension-specific theorem manifests:
   - manifests/dimensions/S0_opposition.yaml
   - manifests/dimensions/S1_circle.yaml or keep existing manifest plus an adapter entry
   - manifests/dimensions/S2_sphere.yaml
   - manifests/dimensions/S3_hypersphere.yaml
   - manifests/dimensions/S4_4sphere.yaml
   - manifests/dimensions/S5_5sphere.yaml
   - manifests/dimensions/S6_6sphere.yaml
   - manifests/dimensions/S7_octonionic.yaml
   - manifests/dimensions/S15_future.yaml

3. Add dimension-specific dictionary files:
   - dictionary/dimensions/S0.yaml
   - dictionary/dimensions/S1.yaml
   - dictionary/dimensions/S2.yaml
   - dictionary/dimensions/S3.yaml
   - dictionary/dimensions/S4_S6.yaml
   - dictionary/dimensions/S7.yaml
   - dictionary/dimensions/warnings.yaml

4. Add paper directories:
   - papers/S1/
   - papers/S2/
   - papers/S3/
   - papers/S4_S6/
   - papers/S7/
   - papers/future/S15/

5. Add Lean module scaffolding, but do not force unproved future files to compile as completed theorems:
   - Circle/Common/
   - Circle/S0/
   - Circle/S1/
   - Circle/S2/
   - Circle/S3/
   - Circle/S4/
   - Circle/S5/
   - Circle/S6/
   - Circle/S7/
   - Circle/Future/S15/

6. Add Python exploratory modules:
   - circle_math/dimensions/
   - circle_math/dimensions/sphere_grid.py
   - circle_math/dimensions/suspension.py
   - circle_math/dimensions/hypersphere.py
   - circle_math/dimensions/quaternion.py
   - circle_math/dimensions/hopf.py
   - circle_math/dimensions/octonion.py

7. Add check scripts:
   - scripts/check_dimension_index.py
   - scripts/check_dimension_imports.py
   - scripts/check_dimension_manifests.py
   - scripts/check_dimension_paper_links.py

8. Add Makefile targets:
   - make dimensioncheck
   - make dimension-roadmap-check

Dimension import policy:
- Common may import only mathlib/basic project-neutral modules.
- S0 may import Common.
- S1 may import Common and S0 only if necessary; existing S¹ core should not be rewritten just to import S0.
- S2 may import Common and S1.
- S3 may import Common, S1, and S2.
- S4 may import Common, S1, S2, and S3.
- S5 may import Common through S4.
- S6 may import Common through S5.
- S7 may import Common through S6 and S3 quaternion modules when appropriate.
- No lower dimension may import a higher dimension.

First milestone:
Create only organization/scaffolding and documents:
- dimension_index.yaml
- dimension manifests with planned theorem ids
- dictionary dimension files
- paper roadmap files
- import policy checker
- paper/dictionary/manifest checker updates

Do not implement S² Lean proofs in the first milestone unless S¹ is already green.

Second milestone:
Implement S² finite combinatorial sphere calculus:
- SuspC(n), the suspension of a finite circle C_n
- SphereGrid(n,r), latitude rings with north/south pole collapse
- Euler characteristic formulas
- latitude rotations that reuse S¹ period/coils
- Paper S2.1 and S2.2 drafts linked to theorem ids

Third milestone:
Implement S³ finite hypersphere calculus:
- Susp(K) for finite 2D sphere meshes
- Susp(SuspC(n)) cell counts
- Euler characteristic χ(S³)=0 for the finite suspension model
- Paper S3.1

Fourth milestone:
Implement S³ quaternion calculus:
- Use Mathlib.Algebra.Quaternion if available.
- Prove or stage unit-quaternion closure, inverse, norm behavior, and noncommutativity examples.
- Paper S3.2

Fifth milestone:
Implement S³ Hopf calculus:
- Python numerical model first.
- Then Lean statements/proofs only where mathlib support is sufficient.
- Show Hopf map lands on S² and is invariant under simultaneous S¹ phase rotation.
- Paper S3.3

Sixth milestone:
Implement general suspension/Euler parity for S⁴-S⁶:
- Prove χ(Susp K)=2-χ(K) for finite cell-count models.
- Derive χ(S^d)=1+(-1)^d for iterated suspensions in the combinatorial model.
- Draft papers for S4/S5/S6 roles without overclaiming special algebraic structure.

Seventh milestone:
Implement S⁷ roadmap and exploratory code:
- Topological S⁷ by iterated suspension.
- Quaternionic Hopf target S³ -> S⁷ -> S⁴.
- Octonion units as exploratory algebra.
- Do not mark octonion theorems proved until a robust no-axiom formalization exists.
- Paper S7.1, S7.2, S7.3 as planned/draft unless proved.

Verification:
Run:
- lake build
- python -m pytest
- python scripts/check_manifest.py
- python scripts/check_dictionary.py
- python scripts/check_dimension_index.py
- python scripts/check_dimension_imports.py
- python scripts/check_dimension_manifests.py
- python scripts/check_dimension_paper_links.py

Stop and report if:
- S¹ breaks.
- lower dimensions import higher dimensions.
- a future theorem is marked proved without a compiled Lean declaration.
- a paper cites a planned/blocked/deferred theorem as proven.
- S² is accidentally modeled as C_n × C_m.
- S³ is described as globally S² × S¹.
- unit octonions are described as a group.
```
