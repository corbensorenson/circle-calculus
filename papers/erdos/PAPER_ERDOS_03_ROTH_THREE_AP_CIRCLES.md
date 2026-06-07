# Circle Calculus Erdos 3: Roth and Three-Term Progressions

Status: polished draft with mathlib-backed theorem bridges and executable arithmetic-progression examples.

## Aim

This paper opens the density-additive-combinatorics lane. Three-term arithmetic progressions are the smallest serious test for whether Circle Calculus can talk rigorously about additive structure, density, and finite interval models without overclaiming progress on open problems.

The current formal seed has two proved Lean bridges:

- `CC-T0066`: `Circle.roth_three_ap_nat_bridge`
- `CC-T0067`: `Circle.roth_number_sublinear_bridge`

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_ERDOS_03_ROTH_THREE_AP_CIRCLES/lean/PaperErdos03.lean
```

The Python examples are:

```text
sidecars/PAPER_ERDOS_03_ROTH_THREE_AP_CIRCLES/python/test_roth_three_ap_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks finite witness searches; Lean declarations determine proof status.

## Theorem Spine

- `CC-T0066`: `Circle.roth_three_ap_nat_bridge`
- `CC-T0067`: `Circle.roth_number_sublinear_bridge`

## Proved Core

`CC-T0066` packages the natural-number form of Roth's theorem from mathlib:

```text
Above the Roth threshold, a dense finite subset of range n is not ThreeAPFree.
```

`CC-T0067` packages the asymptotic Roth-number statement:

```text
rothNumberNat(N) = o(N).
```

These are imported theorem bridges. Circle contributes project-native theorem IDs, sidecars, and executable examples.

## Examples

The Python sidecar checks finite nontrivial three-term arithmetic progressions such as `(0, 2, 4)`, checks small AP-free examples, and records density plus witnesses for a deterministic interval example.

## Why This Matters

Roth is a better excitement target than many famous open Erdos problems because it is deep, respected, and already formalized. Circle can use it to build the missing infrastructure for finite interval models, density, witness search, and eventually cyclic-to-natural transfer.

## Next Program

- Add finite cyclic three-term AP definitions over `C_n`.
- Compare cyclic and natural AP witnesses in bounded examples.
- Add representation-function and density vocabulary before trying Erdos-Turan-style additive-basis questions.

## Guardrail

This paper does not claim a new proof of Roth's theorem or progress on an open Erdos problem. It establishes a rigorous bridge and a finite example layer.
