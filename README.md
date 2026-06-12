# Circle Calculus

**Start here:** the [Circle Calculus Living Book](https://corbensorenson.github.io/circle-calculus/) is the public, interactive textbook for this project. If you only click one link, click that one.

Circle Calculus rebuilds familiar mathematics from one move — *count, and when you run out of room, wrap around* — and keeps every claimed result tied to a machine-checked Lean proof. It is a staged, honest formalization: papers are allowed to be ambitious, but a theorem only counts as proved when a Lean declaration says so.

## What This Is

The project starts from the finite cyclic address space `C_n` (modeled in Lean as `ZMod n`) and builds upward: rotations as addition, coils as repeated rotation, period and closure, orbit decomposition, winding/lift to the natural numbers, scaling and factor structure, and a dimension-indexed ladder of finite sphere scaffolds (`S^0` through `S^7`, with `S^15` as a roadmap).

Every serious concept is meant to be traceable to:

- a human-readable paper in `papers/`,
- a Lean 4 / mathlib declaration in `Circle/` (and per-paper sidecars in `sidecars/`),
- an executable Python reference model in `circle_math/`,
- a shared dictionary entry in `dictionary/`, and
- a status entry in a manifest under `manifests/`.

## What Is Actually Proved

In plain terms — and stated at its true altitude — the proved core is **clean, elementary finite and cyclic mathematics, fully formalized**:

- **Finite-circle arithmetic (S1):** rotation laws, coils, period `= n / gcd(n, k)`, orbit decomposition (`gcd(n, k)` classes), full-coil-iff-coprime, and a substantial scaling/affine theory. These are genuine finite group-theory results proved against mathlib (Lagrange's theorem, additive order, Bézout's identity).
- **Winding and naturals:** the unique winding/residue lift and lifted natural-number addition with carry.
- **A finite sphere ladder (S0–S7):** suspension cell-counts and the Euler-characteristic rule `χ → 2 − χ`, the real-quaternion algebra spine, bounded Hopf-coordinate facts, and a bounded Cayley–Dickson (octonion) model including explicit non-associativity.
- **Classical bridges:** Lean-checked *wrappers* around established mathlib results (Erdős–Ginzburg–Ziv, Cauchy–Davenport, Roth, and others), restated in Circle-facing language. These are not new theorems and not progress on open problems — they are labeled as wrappers.
- **Finite "application" lanes (physics / AI / generative / compute):** these are deliberately modest, honestly named finite models. A "Wilson-loop invariance" theorem here is the fact that a sum of `ZMod n` phases around a closed loop is gauge-independent; an "AI memory-slot" theorem is the fact that an index stays below its bank size and is unchanged by adding a full period. They are correct, useful for keeping the prose honest, and **not** claims about physics or about model quality.
- **Circle AI transfer:** the active AI lane now targets proof-linked recurrence, routing, memory, phase-feature, circulant-mixer, and seed-rule provenance contracts that can be tested in Theseus-Hive under ordinary baselines. This is a benchmark program, not a claim that Circle Calculus has already improved AI systems.

The exhaustive, per-theorem list lives where it belongs — in the manifests (`manifests/theorem_manifest.yaml` and `manifests/dimensions/`, `manifests/applications/`) — and is rendered, with live status, on the Living Book [Theorem Index](https://corbensorenson.github.io/circle-calculus/theorems.html). It is intentionally **not** duplicated here.

## What This Does Not Claim

This repository does not claim to have rebuilt all of mathematics from circles. It does not claim that Python tests or diagrams are proofs, that the physics/AI lanes are physics or model-quality results, that `S^2` has a natural group structure, that `S^3` is globally `S^2 × S^1`, that unit octonions form a group, or that formalization bypasses foundational limits. See `docs/GODEL_AND_LIMITATIONS.md`.

## How To Read It

1. The [Living Book](https://corbensorenson.github.io/circle-calculus/) — the guided learning path, starting with the finite circle.
2. `papers/PAPER_01_FINITE_CIRCLES.md` and its sidecar `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`.
3. `dictionary/circle_dictionary.yaml` for fixed vocabulary.
4. `manifests/theorem_manifest.yaml` for theorem status.
5. `docs/COMPLETION_ROADMAP.md` and `docs/DIMENSIONAL_LADDER.md` for where it is going.
6. `docs/THESEUS_HIVE_AI_TRANSFER.md` for the AI transfer plan into the user's active Theseus-Hive project.

The Living Book's [What "Proved" Means Here](https://corbensorenson.github.io/circle-calculus/what_proved_means.html) page is the one-paragraph contract the whole project lives by.

## Proof Standard

A claim is treated as **proved** only when all of the following hold:

1. it has a theorem id in a manifest under `manifests/`,
2. that id names an exact Lean declaration,
3. its manifest status is `proved` or `lean_proved`,
4. `lake build` succeeds, and
5. `scripts/check_no_fake_proofs.py` finds no forbidden placeholders (`sorry`, `admit`, `axiom`, …).

Anything short of that is `planned`, `exploratory`, or `stated` — never "proved." Python tests and diagrams are executable support, not proofs. Full policy: `docs/PROOF_POLICY.md`.

## Repository Layout

```text
Circle/        Lean 4 / mathlib formalization
circle_math/   Python reference models
dictionary/    Shared vocabulary
docs/          Proof policy and foundational notes
manifests/     Paper and theorem metadata (the canonical theorem index)
papers/        Human-readable papers
sidecars/      Per-paper Lean, Python, and diagram artifacts
site/          The Quarto Living Book
scripts/       Repository validation scripts
tests/         Python regression / property tests
```

## Getting Started

Install Lean via `elan`, then set up Python:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run the full verification suite (the first Lean build fetches and compiles mathlib, so it takes a while):

```bash
make check
```

Useful targets: `make lean` (build the Lean library), `make test` (Python tests), `make sitecheck` (validate the Living Book), `make site-render` (render the book), and `make living-book-check` (everything, including the rendered artifact). See the `Makefile` for the full list.

For the Theseus-Hive AI transfer lane, run:

```bash
make theseus-ai-contracts
```

This writes `site/data/generated/theseus_hive_ai_contracts.json`, a public-safe fixture pack for recurrence, fanout, memory, phase-feature, mixer, and seed-rule experiments.

If the companion Theseus-Hive workspace is present, its report-only consumers are `scripts/circle_ai_contract_consumer.py`, `scripts/circle_ai_private_workload_smoke.py`, `scripts/circle_ai_private_proxy_benchmark.py`, `scripts/circle_ai_real_workload_attachments.py`, and `scripts/circle_ai_scored_private_benchmarks.py`. They treat the Circle pack as private experiment configuration and write YELLOW planning/smoke/proxy/aggregate-attachment/scored-candidate/semantic-context/full-frontier-semantic/recurrence-work-budget/context-memory/phase-feature/route-mixer/router-head-attachment/seed-rule/seed-rule-stress/workflow-rebuild/update-cycle-effort reports until runtime, transfer, or quality results beat ordinary baselines. The active Theseus-Hive trainer also has opt-in pure and residual Circle mixer paths plus an aggregate `circle_router_head_mixer_shadow_training_v1` benchmark; current local traces show compatibility with the baseline router-head trainer, while the keyword-boundary contrastive diagnostic shows pure and residual Circle mixers still trail the no-mixer baseline rather than proving a model-quality, runtime, or memory win.

## License And Citation

Released under the MIT License. If you build on this work, please cite Corben Sorenson and the public repository; GitHub and citation tools can read the recommended citation from `CITATION.cff`.
