# Proof-Depth Audit

`scripts/check_proof_depth_audit.py` is a review aid for spotting Lean declarations whose proof bodies look very small. It is not a sound measure of mathematical depth.

The audit is intentionally non-failing in normal project checks. It flags candidates for human review, then attaches a suggested `review_category` in JSON output and stdout:

- `application_contract_bridge`: theorem packages an engineering contract or certifier bridge.
- `mathlib_bridge_wrapper`: theorem restates or routes an external mathlib theorem through Circle vocabulary.
- `scaffold_or_roadmap_fact`: theorem belongs to dimensional scaffolding or roadmap algebra.
- `metadata_projection`: theorem projects or validates manifest/glyph metadata.
- `finite_physics_contract`: theorem belongs to the finite lattice/gauge contract layer.
- `generative_fixture_contract`: theorem belongs to seed/rule/provenance fixture bookkeeping.
- `core_arithmetic_normalization`: theorem belongs to core finite-circle arithmetic normalization.
- `proof_interface_contract`: theorem belongs to proof-glyph or proof-interface bookkeeping.
- `iff_packaging`: theorem packages an equivalence or one direction of an equivalence.
- `normalization_fact`: theorem proves a definitional normalization, zero, equality, or idempotence fact.
- `review_required`: no clear benign category was inferred.

False positives are expected. A low-depth candidate can still be useful when it is explicitly a wrapper, manifest contract, generated-interface bridge, or normalization lemma. The concern is accumulation: if a research lane adds many `review_required` or contract-wrapper theorems without substantive lemmas nearby, the lane should be reviewed before adding more names.

Useful commands:

```bash
python scripts/check_proof_depth_audit.py
python scripts/check_proof_depth_audit.py --json-out /tmp/proof_depth_audit.json
python scripts/check_proof_depth_audit.py --fail-on-review-required
```

`make sourcecheck` uses `--fail-on-review-required`. Known wrapper, scaffold,
metadata, contract, and normalization categories remain review-only, but a new
low-depth theorem that the heuristic cannot classify must be categorized or
rewritten before the project check passes.

Do not use this audit to downgrade Lean proof status. Lean still decides whether the theorem is formally proved; this audit helps decide whether the theorem is meaningful enough for the project's research narrative.
