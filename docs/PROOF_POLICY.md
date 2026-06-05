# Proof Policy

A theorem is not proved unless:

1. It has a theorem id in `manifests/theorem_manifest.yaml`.
2. It has an exact Lean declaration name.
3. Its manifest status is `proved`.
4. `lake build` succeeds.
5. `scripts/check_no_fake_proofs.py` finds no forbidden proof placeholders.

Python tests and diagrams are executable support, not formal proofs.

