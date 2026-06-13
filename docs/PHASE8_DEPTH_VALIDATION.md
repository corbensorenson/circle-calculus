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

- Prove a real-phase margin theorem or a bounded precursor for RoPE-style rotations. The long-horizon version should connect phase distance, context length, and Diophantine approximation through continued-fraction or three-distance-style bounds. The landed spine now includes the unwrapped one-channel phase-gap formula, lower-bound pair, one-turn endpoint-error bridge, all-nonnegative-full-turn bridge, signed full-turn multiple precursor, turn-separation predicate, no-near-turn consequence, finite bank-level no-near-turn bridge, turn-ratio scaled Diophantine bridge, one-channel plus bank-level finite-context margin consequence theorems, certified-context monotonic transfer, certified-margin downgrade, combined context-plus-margin bank transfer, integer-turn-ratio and natural-rational-turn-ratio no-positive-margin guardrails, a positive reduced-rational `1 / denominator` finite-context margin certificate below the denominator gap, an exact reduced-rational denominator-boundary iff, generated-gap finite-enumeration bridge, floor/ceiling nearest-integer witness bridge, a proof-carrying finite-margin certificate wrapper, a first named rational/discretized `1/4099` context-4096 certificate, a generic rational interval-certificate bridge, interval-certificate margin monotonicity, a first named standard-RoPE channel-0 interval seed for `1 / (2π)`, context `6`, margin `1/8`, strengthened standard-channel seeds through contexts `7`, `8`, `19`, `44`, `57`, `333`, the context-`710`, margin-`1/1024` seed with generated d6 bands plus its proved gap-`710` obstruction, the context-`4096`, margin-`1/131072` seed using 20-decimal `π` bounds and generated cells for gaps `1` through `4095`, a conditional D9 bank-level transfer, a sharper gap-`710` obstruction proving the doubled D9 margin `1/65536` cannot hold for any context containing that gap, the context-`4096`, margin-`1/105000` D10 seed using the same 20-decimal bands plus its `1/104000` obstruction, and the current context-`4096`, margin-`1/104219` D11 seed plus a bank-level transfer and adjacent `1/104218` obstruction (`AIRA-T0029` through `AIRA-T0033`, plus `AIRA-T0037` through `AIRA-T0045`, `AIRA-T0047`, `AIRA-T0050`, and `AIRA-T0053` through `AIRA-T0116`). The Python sidecar now marks the d4 context-333, d6 context-710, conservative d20 context-4096, tighter d20 context-4096, and sharp d20 context-4096 plans as converted to Lean proof. The rational preset is theorem-backed for a declared rational/discretized turn ratio; the standard seed is theorem-backed for the genuine channel-0 turn ratio over one channel and a bounded context only. The next hard step is a full-bank standard-RoPE theorem or sharper channel-wise certificates, not a model-quality claim.
- Upgrade sparse-attention reachability lemmas into coverage iff statements. The sparse lane now has the abstract gap iff (`AIT-T0020`), concrete no-local/no-stride-step uncovered-lag theorem (`AIT-T0021`), dense-local no-gap theorem (`AIT-T0022`), exact local-window threshold (`AIT-T0023`), family-recursion and empty-family controls (`AIT-T0024` through `AIT-T0028`), monotonic lag-preservation under wider local-window or longer path-length budgets (`AIT-T0029` through `AIT-T0032`), a named complete-coverage predicate whose truth is equivalent to having no positive in-context uncovered-lag witness and is preserved by conservative budget increases (`AIT-T0033` through `AIT-T0035`), raw candidate-budget upper-bound accounting before deduplication (`AIT-T0036` through `AIT-T0038`), a context-clipped deduplicated-budget cap (`AIT-T0039` through `AIT-T0042`), an exact theorem-side lag-candidate list whose in-context membership is equivalent to local+stride-family reachability (`AIT-T0043` through `AIT-T0050`), query-indexed predecessor-candidate list/count facts for generated lags (`AIT-T0051` through `AIT-T0054`), no-collision equality criteria for lag and query candidate lists (`AIT-T0055` and `AIT-T0056`), structural conditions that imply those no-collision predicates (`AIT-T0057` and `AIT-T0058`), a concrete single-stride no-wrap numeric sufficient condition (`AIT-T0059` through `AIT-T0062`), a compositional finite-family residue no-collision rule (`AIT-T0063`), a numeric no-wrap head/tail separation condition for the compositional premise (`AIT-T0064`), an inductive ordered separated-family sufficient condition for duplicate-free stride-family residues (`AIT-T0065`), separated-family local/coil plus full lag-candidate no-collision conditions (`AIT-T0066` and `AIT-T0067`), separated-family query no-collision plus exact raw-budget endpoints under predecessor injectivity (`AIT-T0068` through `AIT-T0070`), a numeric local-window-below-context condition that proves predecessor injectivity and removes that abstract assumption from the packaged query/raw-budget endpoint (`AIT-T0071` through `AIT-T0075`), raw-budget survival iff no-collision endpoints for lag and query candidates (`AIT-T0076`, `AIT-T0077`), a finite positive-lag range coverage iff tying complete coverage to membership in the theorem-side candidate list (`AIT-T0078`), and concrete default-plan gap/incomplete-coverage theorems for lag `5` in the `C_120`, local-window `4`, path-length `3`, strides `[7,13]` fixture (`AIT-T0079`, `AIT-T0080`). The sidecar now emits reproducible text/JSON/Markdown result fixtures for the default sparse plan, including covered lags, uncovered gap witnesses, no-collision predicates, and candidate-budget fields. The remaining useful sparse contract is to add richer real-plan sparse configurations and further necessary-and-sufficient coverage or budget theorems where they are honest.
- Add collision counting for finite phase banks. The certifier now reports theorem-backed common-gap and common-gap-multiple families (`AIRA-T0027`, `AIRA-T0028`, and `AIRA-T0034`), exact single-period channel counts backed by the positive period-multiple converse (`AIRA-T0035`), an exact integer-bank total backed by the period-bank LCM criterion (`AIRA-T0036`), the no-unequal-collision pass condition when the LCM reaches the inspected context (`AIRA-T0046`), and a checked LCM fail-witness family when the positive LCM is below context (`AIRA-T0048`, `AIRA-T0049`). The Python certifier now applies that same LCM spine to bounded channel prefixes and selected subfamilies, reporting sufficient subbanks that already distinguish the inspected context under the integer-period model, and includes representative prefix-pass, shared-factor, quantized near-boundary, and interpolation-style scaled-period diagnostic presets. `AIRA-T0051` proves the prefix-to-full-bank bridge, and `AIRA-T0052` proves the unordered selected-subbank bridge. `scripts/phase_bank_certify.py` exposes the exact-only interface for declared positive integer-period banks without emitting real-phase claims.

### 2. External Validation

- Publish findings, not just infrastructure. Run the RoPE certifier against named, reproducible configurations and write the result as a Living Book note.
- Seek one external checkpoint: Lean Zulip, an ML verification workshop, a focused GitHub discussion, or a public issue from someone trying the certifier. The review packet is `docs/ROPE_CERTIFIER_REVIEW_PACKET.md`; the remaining step is the outside request and durable link.
- Build a second proof-carrying AI contract end to end. The landed slice is ring-buffer/KV-cache safety (`AIM-T0059` through `AIM-T0070`): bounded slots, same-slot full-cache overwrite, collision iff divisibility, no collision for positive gaps smaller than cache size, next-overwrite-after-current for retained tokens, an iff between retained-window membership and the non-future plus next-overwrite boundary, the stale-token converse where the next same-slot overwrite is at or before the current token, current-slot distinctness for retained older tokens, pairwise slot distinctness for ordered retained tokens, unordered distinct-token slot distinctness in the same live window, duplicate-free slot maps for retained token batches, and JSON/Markdown result fixtures for the implementation-facing sidecar.

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

`scripts/check_proof_depth_audit.py` scans Lean theorem and lemma declarations for short proof bodies that start with patterns such as `rfl`, `simp`, `constructor`, `Or.inl`, `Or.inr`, simple existential packaging, or projections. The output is review triage only. It can identify places where the repo may be accumulating contract vocabulary instead of theorem content, but it cannot decide whether a theorem is mathematically meaningful. The category guide is `docs/PROOF_DEPTH_AUDIT.md`.

The default standalone mode is still non-failing, because known wrappers and
normalization lemmas are useful review signals rather than proof failures.
`make sourcecheck` runs the audit with `--fail-on-review-required`: the current
corpus has no unclassified low-depth candidates, and future low-depth
declarations must either fit a documented category or be rewritten before the
project check passes. This keeps the guardrail focused on dilution without
pretending that a syntactic heuristic measures mathematical depth.
