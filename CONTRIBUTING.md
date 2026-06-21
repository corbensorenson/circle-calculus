# Contributing To Circle Calculus

Contributions must preserve the proof-status boundary: examples, widgets,
benchmarks, and papers do not make a claim proved. A proved claim needs a
compiled Lean declaration, a theorem manifest entry, and passing checks.

## Add A Theorem

1. Choose the smallest existing Lean module that owns the concept.
2. Add the Lean declaration and proof.
3. Add or update the theorem manifest entry with `id`, `lean_name`, statement,
   dictionary dependencies, paper references, tests, and verification flags.
4. Link the theorem from the relevant paper or sidecar.
5. Run:

```bash
lake build Circle
python scripts/check_manifest.py
python scripts/check_manifest_lean_names.py
python scripts/check_no_fake_proofs.py
python scripts/check_paper_theorem_links.py
```

Do not mark the theorem `proved` until those checks pass.

## Add A Python Model

1. Put stable reusable code under `circle_math/`.
2. Put paper-specific examples under `sidecars/<PAPER_ID>/python/`.
3. Add tests under `tests/` or the relevant sidecar.
4. Keep docstrings clear about whether the code is a reference model,
   executable example, benchmark, or consumer helper.
5. Add public APIs only through `circle_math.core`, `circle_math.contracts`, or
   `circle_math.ai_contracts` when the interface is intended for users.

Run:

```bash
python -m pytest tests -q
```

For focused changes, use the targeted runner documented in
`docs/CHANGE_AWARE_VALIDATION.md`.

## Add A Contract

1. Define the finite structural claim and non-claim boundary first.
2. Add theorem ids for every proof-backed field.
3. Add or extend the contract builder in the application contract layer.
4. Add required consumer fields and readiness checks.
5. Update `docs/CONTRACT_SCHEMA_VERSIONING.md` if schema semantics change.
6. Add tests that validate the pack, consumer readiness, fingerprints, and
   downstream acceptance behavior.

Run:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
python scripts/example_validate_circle_ai_contract_pack_schema.py --summary
python scripts/check_downstream_ci_acceptance_example.py --summary
```

## Add A Paper

1. Create the paper under `papers/`.
2. Add a paper manifest entry with theorem ids, dictionary ids, and sidecar path.
3. Add Lean and Python sidecars when useful.
4. Label unproved claims as planned, exploratory, deferred, or blocked.
5. Add Living Book links only after the paper has a stable source trail.

Run:

```bash
python scripts/check_paper_manifest.py
python scripts/check_paper_source_trails.py
python scripts/check_paper_theorem_links.py
```

## Public Documentation Rule

Every public page that advertises usefulness should state its boundary: proved,
executable, experimental, or speculative. Use the claim-boundary badge pattern
in the Living Book for major user-facing pages.
