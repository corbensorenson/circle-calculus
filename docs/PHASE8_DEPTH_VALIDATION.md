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

- Prove a real-phase margin theorem or a bounded precursor for RoPE-style rotations. The long-horizon version should connect phase distance, context length, and Diophantine approximation through continued-fraction or three-distance-style bounds. The landed precursors are the unwrapped one-channel phase-gap formula, lower-bound pair, one-turn endpoint-error bridge, all-nonnegative-full-turn bridge, signed-full-turn bridge, turn-separation predicate, no-near-turn consequence, finite bank-level no-near-turn bridge, turn-ratio scaled Diophantine bridge, one-channel plus bank-level finite-context margin consequence theorems, certified-context monotonic transfer, certified-margin downgrade, and combined context-plus-margin bank transfer (`AIRA-T0029` through `AIRA-T0033`, plus `AIRA-T0037` through `AIRA-T0045`, `AIRA-T0047`, and `AIRA-T0050`); they deliberately do not claim the Diophantine bound needed for a full real RoPE margin proof.
- Upgrade sparse-attention reachability lemmas into coverage iff statements. The sparse lane now has the abstract gap iff (`AIT-T0020`), concrete no-local/no-stride-step uncovered-lag theorem (`AIT-T0021`), dense-local no-gap theorem (`AIT-T0022`), exact local-window threshold (`AIT-T0023`), family-recursion and empty-family controls (`AIT-T0024` through `AIT-T0028`), monotonic lag-preservation under wider local-window or longer path-length budgets (`AIT-T0029` through `AIT-T0032`), a named complete-coverage predicate whose truth is equivalent to having no positive in-context uncovered-lag witness and is preserved by conservative budget increases (`AIT-T0033` through `AIT-T0035`), raw candidate-budget upper-bound accounting before deduplication (`AIT-T0036` through `AIT-T0038`), a context-clipped deduplicated-budget cap (`AIT-T0039` through `AIT-T0042`), an exact theorem-side lag-candidate list whose in-context membership is equivalent to local+stride-family reachability (`AIT-T0043` through `AIT-T0050`), query-indexed predecessor-candidate list/count facts for generated lags (`AIT-T0051` through `AIT-T0054`), no-collision equality criteria for lag and query candidate lists (`AIT-T0055` and `AIT-T0056`), structural conditions that imply those no-collision predicates (`AIT-T0057` and `AIT-T0058`), a concrete single-stride no-wrap numeric sufficient condition (`AIT-T0059` through `AIT-T0062`), a compositional finite-family residue no-collision rule (`AIT-T0063`), a numeric no-wrap head/tail separation condition for the compositional premise (`AIT-T0064`), an inductive ordered separated-family sufficient condition for duplicate-free stride-family residues (`AIT-T0065`), separated-family local/coil plus full lag-candidate no-collision conditions (`AIT-T0066` and `AIT-T0067`), separated-family query no-collision plus exact raw-budget endpoints under predecessor injectivity (`AIT-T0068` through `AIT-T0070`), and a numeric local-window-below-context condition that proves predecessor injectivity and removes that abstract assumption from the packaged query/raw-budget endpoint (`AIT-T0071` through `AIT-T0075`). The remaining useful sparse contract is a sharper necessary-and-sufficient characterization for when a finite stride-family plan's raw budget survives deduplication.
- Add collision counting for finite phase banks. The certifier now reports theorem-backed common-gap and common-gap-multiple families (`AIRA-T0027`, `AIRA-T0028`, and `AIRA-T0034`), exact single-period channel counts backed by the positive period-multiple converse (`AIRA-T0035`), an exact integer-bank total backed by the period-bank LCM criterion (`AIRA-T0036`), the no-unequal-collision pass condition when the LCM reaches the inspected context (`AIRA-T0046`), and a checked LCM fail-witness family when the positive LCM is below context (`AIRA-T0048`, `AIRA-T0049`). The Python certifier now applies that same LCM spine to bounded channel prefixes, reporting the first prefix that already distinguishes the inspected context under the integer-period model. The remaining depth target is richer representative discretized failure cases and, eventually, formally stated prefix/subfamily selection theorems.

### 2. External Validation

- Publish findings, not just infrastructure. Run the RoPE certifier against named, reproducible configurations and write the result as a Living Book note.
- Seek one external checkpoint: Lean Zulip, an ML verification workshop, a focused GitHub discussion, or a public issue from someone trying the certifier. The review packet is `docs/ROPE_CERTIFIER_REVIEW_PACKET.md`; the remaining step is the outside request and durable link.
- Build a second proof-carrying AI contract end to end. The landed slice is ring-buffer/KV-cache safety (`AIM-T0059` through `AIM-T0068`): bounded slots, same-slot full-cache overwrite, collision iff divisibility, no collision for positive gaps smaller than cache size, next-overwrite-after-current for retained tokens, current-slot distinctness for retained older tokens, pairwise slot distinctness for ordered retained tokens, unordered distinct-token slot distinctness in the same live window, and duplicate-free slot maps for retained token batches.

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
