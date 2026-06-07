# Circle Calculus Erdos 5: Unit-Distance Circulant Graphs

Status: polished draft with mathlib-backed graph bridges and executable cycle/circulant examples.

## Aim

This paper gives Circle Calculus a graph-geometry lane. Famous Erdos unit-distance problems are much harder than finite cycle graphs, so the honest first target is a small proof-carrying graph lab: cycles as circulant graphs, connectedness, and unit-distance embedding vocabulary.

The current formal seed has three proved Lean declarations:

- `CC-T0070`: `Circle.cycle_graph_circulant_bridge`
- `CC-T0071`: `Circle.cycle_graph_connected_bridge`
- `CC-T0072`: `Circle.empty_graph_unit_distance_embedding_bridge`

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_ERDOS_05_UNIT_DISTANCE_CIRCULANT_GRAPHS/lean/PaperErdos05.lean
```

The Python examples are:

```text
sidecars/PAPER_ERDOS_05_UNIT_DISTANCE_CIRCULANT_GRAPHS/python/test_circulant_graph_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks finite graph examples and unit-length regular-polygon edges; Lean declarations determine proof status.

## Theorem Spine

- `CC-T0070`: `Circle.cycle_graph_circulant_bridge`
- `CC-T0071`: `Circle.cycle_graph_connected_bridge`
- `CC-T0072`: `Circle.empty_graph_unit_distance_embedding_bridge`

## Proved Core

`CC-T0070` packages mathlib's cycle/circulant identity:

```text
cycleGraph(n + 1) = circulantGraph({1} : Set (Fin (n + 1))).
```

`CC-T0071` packages connectedness of cycle graphs. `CC-T0072` is a compiled constructor showing that an injection into a metric space gives a unit-distance embedding of the empty graph.

## Examples

The Python sidecar checks that finite cycle edges match the jump-one circulant graph, then places a regular polygon at radius `1 / (2 sin(pi/n))` so each cycle edge has unit length. This is an executable graph lab, not a proof of any hard unit-distance theorem.

## Why This Matters

This lane gives Circle Math a conservative entry into graph and geometry language. It is useful because circulant graphs are genuinely cyclic, visual, and connected to both combinatorics and applications. It also prevents premature claims about deep Euclidean unit-distance problems.

## Next Program

- Add finite circulant graph parameters and examples beyond jump set `{1}`.
- Add Lean bridges for Cayley graph translation invariance if useful.
- Add explicit Euclidean embeddings only when the theorem statement is formal, not only a drawing.

## Guardrail

This paper does not claim progress on hard unit-distance or distinct-distance problems. It builds the vocabulary and proof boundary for future graph work.
