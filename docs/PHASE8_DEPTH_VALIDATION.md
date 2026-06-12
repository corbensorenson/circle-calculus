# Phase VIII: Depth, External Validation, And Contract Hardening

Phase VIII is the anti-scaffolding phase. Its purpose is to turn the strongest existing Circle Calculus artifacts into externally useful, mathematically deeper, and publicly checkable deliverables.

The phase is motivated by a simple diagnosis: more fixtures, named definitions, and manifest entries do not by themselves raise the project. The next gains come from real theorem content, results on real configurations, outside review, and proof-discipline tooling that can detect ceremonial proofs before they dilute the corpus.

## North Star

Ship proof-carrying contracts that a non-Lean engineer can use, while pushing the formal spine beyond elementary finite bookkeeping.

The first flagship remains the RoPE position-distinguishability certifier:

```text
real or discretized RoPE configuration
  -> theorem-linked certificate
  -> exact discrete collision or distinguishability result
  -> numerical real-phase margin report
  -> Living Book explanation
  -> paper and Lean source trail
```

The next step is not another broad list of AI ideas. The next step is depth: turn the real-phase margin caveat into a theorem program, run the certifier on real model-like configurations, and add collision-counting and coverage-iff results that expose gaps as well as examples.

## Workstreams

### 1. Mathematical Depth

- Prove a real-phase margin theorem or a bounded precursor for RoPE-style rotations. The long-horizon version should connect phase distance, context length, and Diophantine approximation through continued-fraction or three-distance-style bounds. The landed precursors are the unwrapped one-channel phase-gap formula, lower-bound pair, one-turn endpoint-error bridge, all-nonnegative-full-turn bridge, and signed-full-turn bridge (`AIRA-T0029` through `AIRA-T0033`); they deliberately do not claim the Diophantine bound needed for a full real RoPE margin proof.
- Upgrade sparse-attention reachability lemmas into coverage iff statements. A useful contract should characterize which lags are covered and which are not, with candidate-budget accounting.
- Add collision counting for finite phase banks. The certifier now reports theorem-backed common-gap and common-gap-multiple families (`AIRA-T0027`, `AIRA-T0028`, and `AIRA-T0034`), exact single-period channel counts backed by the positive period-multiple converse (`AIRA-T0035`), and an exact integer-bank total backed by the period-bank LCM criterion (`AIRA-T0036`). The remaining depth target is richer reporting for bounded bank subfamilies and representative failure cases.

### 2. External Validation

- Publish findings, not just infrastructure. Run the RoPE certifier against named, reproducible configurations and write the result as a Living Book note.
- Seek one external checkpoint: Lean Zulip, an ML verification workshop, a focused GitHub discussion, or a public issue from someone trying the certifier.
- Build a second proof-carrying AI contract end to end. The first landed slice is ring-buffer/KV-cache safety (`AIM-T0059` through `AIM-T0063`): bounded slots, same-slot full-cache overwrite, collision iff divisibility, no collision for positive gaps smaller than cache size, and next-overwrite-after-current for retained tokens.

### 3. Engineering Hardening

- Clean root clutter intentionally. The original browser/Codex handoff directories now live under `archive/handoffs/`; curated docs remain the front door for current project state.
- Keep CI visible to readers. The README should expose the GitHub Actions proof/check badge when the workflow is stable.
- Add a vacuity/proof-depth guard. The project already checks for fake proofs; Phase VIII adds a heuristic guard that flags theorem proofs that are only bare constructors, projections, or one-step wrappers unless they are explicitly classified as wrappers or metadata contracts. The first version is `scripts/check_proof_depth_audit.py`, a non-failing syntactic audit wired into `make sourcecheck`; it reports review candidates without treating the heuristic as a formal depth theorem.

### 4. Communication

- Keep the README front door short. Detailed AI benchmark plumbing belongs in focused docs, papers, or generated result notes.
- Add an ML-engineer quickstart for the certifier that never requires reading Lean code.
- Lead the application path of the Living Book with the certifier demo: useful contract first, foundations immediately after, and limitations always visible.

## Acceptance Criteria

Phase VIII has real progress only when at least one of these lands:

- a Lean-proved RoPE real-phase theorem or bounded quantitative precursor that is more than definitional assembly;
- a sparse-attention coverage iff with a converse or gap certificate;
- a collision-counting theorem and Python certifier output that cites it;
- a public RoPE results note generated from reproducible certifier runs;
- an externally reviewed checkpoint with a durable link or issue;
- a second proof-carrying AI contract, preferably KV-cache/ring-buffer safety;
- a proof-depth/vacuity guard wired into `make check`.

## Guardrails

- Do not claim real-valued RoPE exact collisions when the formal object is a discretized integer-period phase bank.
- Do not call numerical phase-margin scans formal proofs.
- Do not claim model-quality, context-length, speed, memory, or perplexity improvement from a contract.
- Do not add theorem names merely to raise manifest count.
- Do not move handoff directories without updating the docs that reference them.
- Do not treat external validation as authority over Lean proof status; it is a reality check on usefulness and communication.

The machine-readable target registry is `manifests/phase8_depth_validation.yaml`, checked by `scripts/check_phase8_targets.py`.

## Proof-Depth Audit Boundary

`scripts/check_proof_depth_audit.py` scans Lean theorem and lemma declarations for short proof bodies that start with patterns such as `rfl`, `simp`, `constructor`, `Or.inl`, `Or.inr`, simple existential packaging, or projections. The output is review triage only. It can identify places where the repo may be accumulating contract vocabulary instead of theorem content, but it cannot decide whether a theorem is mathematically meaningful.

The default mode is intentionally non-failing. A future Phase VIII pass can add allowlists, proof-kind metadata, or `--strict` use once false positives have been reviewed and documented.
