# Circle Calculus / Coil Mathematics — Codex Master Goal

Paste the following into Codex as the master `/goal`.

```text
/goal Build the Circle Calculus research repository: a formal mathematics project with a versioned dictionary, theorem manifest, Lean 4/mathlib machine proofs for the finite-circle core, Python reference models and tests for executable exploration, paper drafts that cite the exact formal theorem names they depend on, and CI checks proving the repository is internally consistent.

Outcome:
1. Create a repository named circle-calculus.
2. Implement Circle Calculus v0 around finite marked circles, rotations, coils, closure, period, gcd orbit structure, prime full-coil behavior, scaling/invertibility, lifted winding, and glyph/proof metadata.
3. Use Lean 4 + mathlib as the primary proof checker. A theorem is not “proved” unless Lean builds it without sorry/admit/axiom/unsafe in the proved core.
4. Use Python only for executable reference models, examples, property tests, visualizations, manifest validation, and paper automation. Python tests are not formal proofs.
5. Maintain a single theorem_manifest.yaml. Every theorem in the papers must link to a manifest theorem id and exact Lean theorem name. Every manifest theorem must have a status: planned, stated, proved, blocked, or deferred.
6. Maintain a versioned dictionary. Every major term used in papers or code must have a dictionary entry with id, definition, intuition, dependencies, formal model, rewrite/normalization rules, theorem dependencies, and forbidden meanings.
7. Draft the full paper roadmap, but only mark papers as formally complete when their theorem dependencies are proved.
8. Include a Gödel/limitations section: Circle Calculus does not escape incompleteness. The project aims for an alternative machine-checkable foundation/encoding/translation layer, not absolute omniscience.
9. Implement CI commands so success is auditable.

Verification surface:
- `lake build` succeeds.
- `python -m pytest` succeeds.
- `python scripts/check_manifest.py` succeeds.
- `python scripts/check_dictionary.py` succeeds.
- `python scripts/check_no_fake_proofs.py` succeeds.
- `python scripts/check_paper_theorem_links.py` succeeds.
- No proved Lean theorem contains `sorry`, `admit`, unresolved `by?`, unapproved `axiom`, or unapproved `unsafe`.
- Every paper theorem reference resolves to a theorem id in theorem_manifest.yaml.
- Every theorem id marked proved resolves to a compiled Lean declaration.
- Every dictionary id referenced by manifests or papers exists.

Constraints:
- Do not claim that Circle Calculus replaces all mathematics until formal interpretability and translation layers are written and checked.
- Do not call Python property tests “proofs.”
- Do not use diagrams as proofs unless the diagram compiles to a formal proof term.
- Do not smuggle Euclidean geometry into v0. v0 circles are finite cyclic address spaces, not metric circles.
- Do not introduce infinity in v0 except as future roadmap. Continuous circles, real numbers, topology, and calculus belong to later papers.
- Prefer Lean 4 + mathlib for v0. Do not dual-target Rocq/Coq until the Lean v0 core is complete.
- Keep speculative concepts in `docs/speculative/` or manifest status `deferred`.

Iteration policy:
- Work in small verified increments.
- After each increment, run the verification commands.
- If a proof is blocked, leave the theorem in status `blocked`, document the exact blocker and smallest failing Lean statement, then proceed to an adjacent theorem only if it does not depend on the blocker.
- If a definition needs to change, update dictionary, manifest, Python model, Lean code, and paper references together.
- Prefer provable minimal definitions over poetic definitions. Preserve poetic/metaphysical language only in motivation sections, never as formal definitions.

Blocked stop condition:
- Stop and report if Lean/mathlib cannot be installed, if the theorem statements are inconsistent, if a claimed proof requires an unapproved axiom, or if the definitions make the intended theorem false. Include the failed command, the exact error, attempted fixes, and the smallest next input needed.
```

## First task after setting the goal

Ask Codex to create the repository skeleton and the v0 manifest first, before writing papers.

```text
Create only the repository skeleton, dictionary schema, theorem manifest, Python reference model, v0 Lean module layout, CI scripts, and Paper 1 outline. Do not draft all papers yet. The first passing milestone is: dictionary checks pass, manifest checks pass, Python tests pass, and Lean contains at least the rotation identity/composition/inverse theorems with no sorry.
```
