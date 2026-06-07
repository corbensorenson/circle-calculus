# Circle Calculus Erdos 4: Hales-Jewett and Ramsey Lines

Status: polished draft with mathlib-backed Ramsey theorem bridges and executable finite examples.

## Aim

This paper gives Circle Calculus a Ramsey-theory lane. The project already has finite cyclic address spaces; this lane asks how far "structured lines in finite grids" can be made visible through formal theorem bridges and small search fixtures.

The current formal seed has two proved Lean bridges:

- `CC-T0068`: `Circle.hales_jewett_bridge`
- `CC-T0069`: `Circle.van_der_waerden_homothetic_bridge`

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_ERDOS_04_HALES_JEWETT_RAMSEY_CIRCLES/lean/PaperErdos04.lean
```

The Python examples are:

```text
sidecars/PAPER_ERDOS_04_HALES_JEWETT_RAMSEY_CIRCLES/python/test_ramsey_hj_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks tiny monochromatic-line searches; Lean declarations determine proof status.

## Theorem Spine

- `CC-T0068`: `Circle.hales_jewett_bridge`
- `CC-T0069`: `Circle.van_der_waerden_homothetic_bridge`

## Proved Core

`CC-T0068` packages mathlib's Hales-Jewett theorem:

```text
For finite alphabet and finite color set, a sufficiently high-dimensional word cube has a monochromatic combinatorial line.
```

`CC-T0069` packages the homothetic-copy consequence:

```text
For any finite shape S in an additive commutative monoid and any finite coloring,
there is a monochromatic copy a*S + b with a > 0.
```

## Examples

The Python sidecar brute-forces that all binary colorings of nine points contain a monochromatic 3-term AP, finds a monochromatic homothetic copy of `(0, 1, 2)` in a parity coloring, and finds a tiny Hales-Jewett combinatorial line in a binary word square.

## Why This Matters

Ramsey theory is a respected route for showing unavoidable structure. This lane lets Circle Math teach a strong theorem with finite searches that users can inspect, while keeping the formal proof source in Lean.

## Next Program

- Add visual word-cube line widgets for the Living Book.
- Add cyclic colorings and compare ordinary APs with wraparound APs.
- Keep finite searches as examples unless a Lean theorem is added.

## Guardrail

This paper does not claim a new Hales-Jewett or Van der Waerden proof. It provides proof-linked Circle-facing theorem handles and small executable examples.
