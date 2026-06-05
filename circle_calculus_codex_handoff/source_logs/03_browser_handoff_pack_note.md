I made you a **Codex handoff pack** with the master `/goal`, staged goals, repo structure, formal core spec, dictionary schema, theorem manifest schema, paper rules, CI policy, Python reference test plan, and Gödel/limitations policy.

Download it here:

[Download the Circle Calculus Codex handoff pack](sandbox:/mnt/data/circle_calculus_codex_handoff.zip)

## The most important decision

Do **not** give Codex one vague goal like:

```text
/goal Write all of Circle Mathematics and prove everything.
```

That is too large and too easy for it to fake progress.

Give it a **completion contract**: exact repo artifacts, exact proof commands, exact forbidden shortcuts, exact theorem manifest rules, exact staged milestones. OpenAI’s own Codex Goals guidance says a good goal should define the outcome, verification surface, constraints, boundaries, iteration policy, and blocked stop condition. ([OpenAI Developers][1])

## The correct proof stack

Use:

```text
Lean 4 + mathlib = formal machine proofs
Python = executable examples, property tests, visualizations, manifest validation
Papers = human-facing explanations linked to exact theorem ids
Dictionary = stable shared vocabulary
Theorem manifest = source of truth for proof status
```

Lean/mathlib is the best first target because mathlib is a large formalized mathematics library written in Lean and designed for reusable mathematical research foundations. ([Lean Language][2])

Python tests are useful, but they are **not proofs**. The handoff pack says that explicitly.

## The v0 formal core Codex should build first

The finite-circle core should be formalized as:

```lean
C n := ZMod n
rot n k x := x + (k : ZMod n)
period n k := addOrderOf (k : ZMod n)
```

This is not arbitrary. Mathlib already has the crucial theorem shape we want: `ZMod.addOrderOf_coe`, which states that the additive order of `a` in `ZMod n` is `n / gcd n a` when `n ≠ 0`. That gives the clean formal backbone for your coil-period theorem. ([Lean Community][3])

The first serious theorem set is:

```text
CC-T0001 rot_zero
CC-T0002 rot_comp
CC-T0003 rot_inverse_left
CC-T0004 period_eq_n_div_gcd
CC-T0005 prime_full_coil
```

Paper 1 is not “done” until those theorem ids are actually proved in Lean and the repo passes CI.

## The master `/goal` is in the zip

The file to paste into Codex is:

```text
CODEX_MASTER_GOAL.md
```

It includes this core contract:

```text
A theorem is not “proved” unless Lean builds it without sorry/admit/axiom/unsafe in the proved core.
```

and:

```text
Every theorem in the papers must link to a theorem manifest id and exact Lean theorem name.
```

That is the main safeguard against fake rigor.

## Use staged goals after the master goal

The pack also includes:

```text
CODEX_STAGE_GOALS.md
```

I strongly recommend this order:

1. **Stage 0:** Create repo skeleton, schemas, manifest, dictionary, Python model, tests, CI, Paper 1 outline.
2. **Stage 1:** Prove rotation identity/composition/inverse in Lean.
3. **Stage 2:** Prove the period theorem using `ZMod.addOrderOf_coe`.
4. **Stage 3:** Prove prime full-coil behavior.
5. **Stage 4:** Complete Paper 1 only after Lean proofs pass.
6. **Stage 5:** Add winding/lifted circles and natural numbers.

This avoids the common failure mode where Codex writes beautiful papers and half-real proof files that do not actually build.

## The pack contains

| File                                       | Purpose                                        |
| ------------------------------------------ | ---------------------------------------------- |
| `CODEX_MASTER_GOAL.md`                     | Main pasteable Codex `/goal`                   |
| `CODEX_STAGE_GOALS.md`                     | Smaller milestone goals                        |
| `REPO_STRUCTURE.md`                        | Recommended repository layout and make targets |
| `FORMAL_CORE_V0.md`                        | Definitions, theorem targets, Lean strategy    |
| `PYTHON_REFERENCE_SPEC.md`                 | Python reference model and tests               |
| `dictionary/circle_dictionary.schema.json` | Machine-checkable dictionary schema            |
| `dictionary/circle_dictionary.yaml`        | Initial dictionary entries                     |
| `manifests/theorem_manifest.schema.json`   | Machine-checkable theorem manifest schema      |
| `manifests/theorem_manifest.yaml`          | Initial theorem list                           |
| `PAPER_RULES_AND_TEMPLATE.md`              | Paper template and proof-linking policy        |
| `PAPER_ROADMAP.md`                         | Full first-to-last paper roadmap               |
| `GODEL_AND_LIMITATIONS.md`                 | Required honesty about Gödel/incompleteness    |
| `CI_AND_VERIFICATION.md`                   | Exact verification contract                    |

## The key anti-BS rules I put in

These are the rules that matter most:

```text
No paper theorem can be called proven unless it has:
1. A theorem id.
2. A Lean theorem name.
3. Status `proved` in theorem_manifest.yaml.
4. A passing Lean build.
5. No sorry/admit/unapproved axiom/unsafe.
```

```text
No diagram is a proof unless it compiles to a formal proof term.
```

```text
No Python property test is a formal proof.
```

```text
No infinite/continuous/Euclidean circle claims in v0.
```

```text
No claim that Circle Calculus escapes Gödel.
```

The Gödel policy is important because once the system can represent arithmetic, it inherits the usual incompleteness boundaries. Gödel-style encoding is useful here, but it is not an escape hatch.

## My recommended first Codex command

After uploading or pasting the handoff pack into a repo context, use this first:

```text
/goal Create only the repository skeleton, dictionary schema, theorem manifest, Python reference model, v0 Lean module layout, CI scripts, and Paper 1 outline. Do not draft all papers yet. The first passing milestone is: dictionary checks pass, manifest checks pass, Python tests pass, and Lean contains at least the rotation identity/composition/inverse theorem targets with no theorem marked proved unless lake build passes.
```

Then use the staged goals.

The biggest correctness move is to make Codex earn the right to write Paper 1 by first making the proof and manifest machinery real.

[1]: https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex "Using Goals in Codex"
[2]: https://lean-lang.org/use-cases/mathlib/ "Mathlib: A Foundation for Formal Mathematics Research and Verification — Lean Lang "
[3]: https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/ZMod/Basic.html?utm_source=chatgpt.com "Mathlib.Data.ZMod.Basic"
