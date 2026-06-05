# Circle Calculus Handoff - Start Here

This folder is the working handoff for the Circle Calculus / Coil Mathematics project. It contains the original browser discussion logs, the generated Codex handoff pack, and the initial formalization policy.

## Source Logs

The original pasted browser output has been preserved as Markdown here:

1. `source_logs/01_strategy_barriers_and_prototype.md`
   - Conceptual strategy for starting with finite marked circles.
   - Core layers: finite circle arithmetic, lifted circles/counting, then infinite/continuous circles.
   - Main barriers: hidden geometry assumptions, infinity, irrational rotations, loss of information modulo `n`, visual proof traps, Gödel boundaries, and continuum issues.
   - Suggested first prototype and first paper shape.

2. `source_logs/02_paper_roadmap_dictionary_and_success_criteria.md`
   - Full seven-volume paper roadmap with 37 proposed papers.
   - Shared dictionary plan and first draft vocabulary.
   - Success criteria for progressively stronger versions of Circle Calculus.
   - Minimum theorem sets for the first three papers.

3. `source_logs/03_browser_handoff_pack_note.md`
   - Browser-generated explanation of the handoff pack.
   - Recommends Lean 4 + mathlib for formal proofs, Python for executable tests and visualizations, papers for human-facing exposition, and dictionary/manifest files as the shared source of truth.

## Handoff Pack Files

Use these files as the current project contract:

- `CODEX_MASTER_GOAL.md`: the complete Codex goal contract.
- `CODEX_STAGE_GOALS.md`: staged implementation milestones.
- `REPO_STRUCTURE.md`: expected repository layout and commands.
- `FORMAL_CORE_V0.md`: finite-circle formal core and theorem targets.
- `PYTHON_REFERENCE_SPEC.md`: executable Python reference model plan.
- `PAPER_ROADMAP.md`: concise paper roadmap.
- `PAPER_RULES_AND_TEMPLATE.md`: paper template and proof-linking rules.
- `CI_AND_VERIFICATION.md`: verification commands and anti-fake-proof checks.
- `GODEL_AND_LIMITATIONS.md`: required limitations policy.
- `dictionary/`: dictionary schema and initial entries.
- `manifests/`: theorem manifest schema and initial theorem list.

## Working Interpretation

The serious project target is not to claim that circles magically replace all mathematics. The target is to build a precise formal system where finite circular structures, coils, rotations, periods, windings, glyphs, and proofs have machine-checkable syntax and semantics.

The v0 foundation is deliberately narrow:

- `C_n` is a finite cyclic address space, modeled by `ZMod n`.
- A node is an element of `C_n`.
- A rotation is addition by a stride.
- A coil is the orbit of repeated rotation.
- A period is the least positive return time, expected to equal `n / gcd(n,k)` for `n != 0`.
- A prime circle has full-coil behavior for every stride `0 < k < p`.

Continuous circles, real numbers, topology, trigonometry, and calculus are later layers, not v0 assumptions.

## Immediate Implementation Track

The safest next step is to turn the handoff pack into a real repository skeleton and make the proof machinery auditable before writing papers.

Recommended first milestone:

1. Create the Lean 4 project structure.
2. Add the finite-circle v0 module.
3. Add the Python reference package and tests.
4. Add manifest and dictionary validators.
5. Add no-fake-proof checks for `sorry`, `admit`, unapproved `axiom`, and unapproved `unsafe`.
6. Draft only Paper 1's outline.
7. Prove only the first rotation theorems before marking anything as proved.

The first target theorem ids are:

- `CC-T0001`: `Circle.rot_zero`
- `CC-T0002`: `Circle.rot_comp`
- `CC-T0003`: `Circle.rot_inverse_left`
- `CC-T0004`: `Circle.period_eq_n_div_gcd`
- `CC-T0005`: `Circle.prime_full_coil`

The key discipline is that a theorem is not considered proved unless Lean builds it and the manifest records the exact compiled Lean theorem name.
