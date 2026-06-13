# Circle Calculus

[![CI](https://github.com/corbensorenson/circle-calculus/actions/workflows/ci.yml/badge.svg)](https://github.com/corbensorenson/circle-calculus/actions/workflows/ci.yml)
[![Deploy Living Book](https://github.com/corbensorenson/circle-calculus/actions/workflows/pages.yml/badge.svg)](https://github.com/corbensorenson/circle-calculus/actions/workflows/pages.yml)

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
- **Proof-carrying AI contracts:** the active AI lane now targets checked architecture facts: RoPE position distinguishability, KV-cache ring-buffer safety, sparse-attention coverage and gap witnesses, recurrence schedules, and circulant/block-cyclic mixer laws. The flagship public artifact is the RoPE position-distinguishability certifier, followed by KV-cache ring-buffer and sparse-attention coverage contracts; none is a claim that Circle Calculus improves model quality, context length, speed, or memory.

The exhaustive, per-theorem list lives where it belongs — in the manifests (`manifests/theorem_manifest.yaml` and `manifests/dimensions/`, `manifests/applications/`) — and is rendered, with live status, on the Living Book [Theorem Index](https://corbensorenson.github.io/circle-calculus/theorems.html). It is intentionally **not** duplicated here.

## What This Does Not Claim

This repository does not claim to have rebuilt all of mathematics from circles. It does not claim that Python tests or diagrams are proofs, that the physics/AI lanes are physics or model-quality results, that `S^2` has a natural group structure, that `S^3` is globally `S^2 × S^1`, that unit octonions form a group, or that formalization bypasses foundational limits. See `docs/GODEL_AND_LIMITATIONS.md`.

## How To Read It

1. The [Living Book](https://corbensorenson.github.io/circle-calculus/) — the guided learning path, starting with the finite circle.
2. `papers/PAPER_01_FINITE_CIRCLES.md` and its sidecar `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`.
3. `dictionary/circle_dictionary.yaml` for fixed vocabulary.
4. `manifests/theorem_manifest.yaml` for theorem status.
5. `docs/COMPLETION_ROADMAP.md` and `docs/DIMENSIONAL_LADDER.md` for where it is going.
6. The Living Book [AI contract ladder](https://corbensorenson.github.io/circle-calculus/chapters/applications/ai_contract_ladder.html) for the guided sequence through proof-carrying RoPE, KV-cache, sparse-attention, recurrence, and mixer contracts.
7. `docs/ROPE_CERTIFIER_QUICKSTART.md`, `docs/ROPE_CERTIFIER_REVIEW_PACKET.md`, `papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md`, and `scripts/rope_certify.py` for the first externally usable AI contract.
8. The Living Book [KV-cache ring-buffer lesson](https://corbensorenson.github.io/circle-calculus/chapters/applications/kv_cache_ring_buffer.html), `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`, and `sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py` for the second standalone AI contract.
9. The Living Book [sparse-attention coverage lesson](https://corbensorenson.github.io/circle-calculus/chapters/applications/sparse_attention_contract.html), `scripts/stride_family_certify.py`, and `sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py` for the third standalone AI contract.
10. `docs/PHASE8_DEPTH_VALIDATION.md` for the current depth-and-validation push: RoPE real-phase theorem work, sparse coverage iffs, collision counting, KV-cache safety, external review, and proof-depth guardrails.
11. `docs/THESEUS_HIVE_AI_TRANSFER.md` for the optional private-transfer lane; it is not the public proof standard.

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

For the proof-carrying RoPE certifier, run:

```bash
python scripts/rope_certify.py --head-dim 128 --base 10000 --context 32768 --tolerance 1e-6
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
```

The certifier emits theorem ids, Lean declaration names, exact discrete pass/fail, sample colliding pairs when present, a proof-layer inventory, and a separate numerical real-phase margin report. Exact pass/fail is for the declared integer-period phase-bank model; it is not a language-model quality, context-length, speed, or memory claim. The exact phase-bank CLI includes quantized and interpolation-style boundary diagnostics. The real-phase proof program now reduces finite margin checks to generated gaps, floor/ceiling witnesses, and rational interval certificates; it includes one theorem-backed rational/discretized `1/4099` context-4096 certificate plus genuine standard-RoPE channel-0 interval seeds for `1 / (2π)`, including context `4096` at margin `1/104219` and context `8192` at margin `1/104220`, while separately proving that the older `1/1024`, doubled D9 `1/65536`, nearby D10 `1/104000`, and adjacent D11 `1/104218` margins cannot extend once gap `710` is in scope. The bracket theorem packages the useful engineering reading: `1/104219` is Lean-proved for the 4k channel-0 seed, while every margin at or above `1/104218` is Lean-refuted for that context.

For the proof-carrying KV-cache ring-buffer certificate, run:

```bash
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py --format markdown
```

The sidecar emits theorem ids, Lean declaration names, a finite slot/window certificate, and a retained-batch distinctness certificate. It proves finite ring-buffer indexing and overwrite-window facts only; it is not a paging-policy, throughput, memory-saving, retrieval-quality, implementation-correctness, deployment-safety, or model-quality claim.

For the proof-carrying sparse-attention coverage certificate, run:

```bash
python scripts/stride_family_certify.py --context 120 --strides 7,13 --path-length 3 --local-window 4
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py --format markdown
```

The sparse certificate emits theorem ids, covered lags, a theorem-side uncovered-lag list, no-collision budget predicates, and candidate-count fields. It proves finite candidate-set coverage, gap-list membership/counting, and budget facts only; it is not an attention-quality, long-context, throughput, runtime, memory-use, or model-quality claim.

For the optional Theseus-Hive AI transfer lane, run:

```bash
make theseus-ai-contracts
make theseus-ai-feedback
```

This writes `site/data/generated/theseus_hive_ai_contracts.json`, a public-safe fixture pack for recurrence, fanout, memory, phase-feature, mixer, and seed-rule experiments.
The feedback target writes `site/data/generated/theseus_hive_ai_feedback_summary.json` from a sanitized Theseus-Hive handoff when present, or an explicit missing-state placeholder otherwise.
Detailed private-transfer plumbing belongs in `docs/THESEUS_HIVE_AI_TRANSFER.md`. It is optional, aggregate-only, and remains separate from the public proof-carrying contract lane.

## License And Citation

Released under the MIT License. If you build on this work, please cite Corben Sorenson and the public repository; GitHub and citation tools can read the recommended citation from `CITATION.cff`.
