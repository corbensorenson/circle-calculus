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

- Prove a real-phase margin theorem or a bounded precursor for RoPE-style rotations. The long-horizon version should connect phase distance, context length, and Diophantine approximation through continued-fraction or three-distance-style bounds. The first landed precursor is the unwrapped one-channel phase-gap formula and lower-bound pair (`AIRA-T0029`, `AIRA-T0030`); it deliberately does not claim a circular modulo-full-turn margin proof.
- Upgrade sparse-attention reachability lemmas into coverage iff statements. A useful contract should characterize which lags are covered and which are not, with candidate-budget accounting.
- Add collision counting for finite phase banks. The certifier should eventually report not only whether a collision exists, but how many colliding pairs exist in a context and how the count follows from the period bank.

### 2. External Validation

- Publish findings, not just infrastructure. Run the RoPE certifier against named, reproducible configurations and write the result as a Living Book note.
- Seek one external checkpoint: Lean Zulip, an ML verification workshop, a focused GitHub discussion, or a public issue from someone trying the certifier.
- Build a second proof-carrying AI contract end to end. The best next candidate is ring-buffer/KV-cache safety: no overwrite before read, no stale read under declared policy, and modular-index assumptions made explicit.

### 3. Engineering Hardening

- Clean root clutter intentionally. Move archival handoff directories only after their references are updated or replaced by curated docs.
- Keep CI visible to readers. The README should expose the GitHub Actions proof/check badge when the workflow is stable.
- Add a vacuity/proof-depth guard. The project already checks for fake proofs; Phase VIII adds a heuristic guard that flags theorem proofs that are only bare constructors, projections, or one-step wrappers unless they are explicitly classified as wrappers or metadata contracts.

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
