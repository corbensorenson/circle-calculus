# Smaller Codex Goals

Do not ask Codex to complete the entire research program in one run. Use staged goals.

## Stage 0 — Skeleton

```text
/goal Create the circle-calculus repository skeleton, dictionary schema, theorem manifest schema, initial dictionary entries, v0 theorem manifest, Python reference model, pytest suite, Lean module layout, CI scripts, and Paper 1 outline. Verified by python manifest/dictionary checks and pytest. Lean files may contain only definitions and the first rotation theorem target, but no theorem may be marked proved unless lake build passes.
```

## Stage 1 — Rotation core

```text
/goal Prove the v0 rotation core in Lean: rot_zero, rot_comp, and rotation inverse. Verified by lake build, no sorry/admit/axiom/unsafe in Circle/Core, theorem_manifest.yaml marking only these theorem ids proved, and matching Python tests passing.
```

## Stage 2 — Period theorem

```text
/goal Prove period(n,k)=n/gcd(n,k) for finite C_n using Lean 4/mathlib, preferably through ZMod.addOrderOf_coe. Verified by lake build, theorem manifest update, no fake proofs, and Python property tests over bounded n,k.
```

## Stage 3 — Prime full coils

```text
/goal Prove the prime full-coil theorem from the period theorem: if p is prime and 0<k<p then stride k on C_p has period p. Verified by lake build, manifest update, paper theorem table update, and Python tests over primes <= 257.
```

## Stage 4 — Paper 1

```text
/goal Complete Paper 1 as a rigorous draft. It must define finite circles, rotations, coils, closure, period, and prime full-coil behavior; every formal theorem must cite a manifest id and Lean name; all examples must be generated or checked by Python; limitations must state that v0 is finite and non-geometric. Verified by paper link checker, dictionary checker, manifest checker, lake build, and pytest.
```

## Stage 5 — Winding and natural numbers

```text
/goal Implement lifted circles with winding/residue decomposition and prove uniqueness plus addition-as-path-concatenation. Verified by Lean proofs, Python tests, dictionary entries, manifest updates, and Paper 2 draft.
```
