# Circle Graph Coverage

Claim boundary: this page proves finite direct positive-lag coverage for
declared local-window plus stride-family circle graphs. It does not prove sparse
attention quality, graph optimality, speed, memory savings, long-context
capability, or deployment behavior.

## Motivation

Sparse attention is naturally graph-shaped: tokens are vertices, and the
attention mask chooses edges. Relevant research includes strided/fixed sparse
patterns in [Sparse Transformer](https://arxiv.org/abs/1904.10509), local plus
global patterns in [Longformer](https://arxiv.org/abs/2004.05150), local/random/
global graph patterns in [BigBird](https://arxiv.org/abs/2007.14062), dynamic
content routing in [Routing Transformer](https://arxiv.org/abs/2003.05997), and
recent periodic sparse attention work such as
[Periodic Sparse Transformers](https://arxiv.org/html/2511.10696v2).

Circle Calculus formalizes a conservative finite core:

```text
vertices = 0, 1, ..., context-1
edge(query, lag) = query -> query - lag mod context
lag generators = local lags plus stride-step residues
coverage = every positive lag 1..context-1 is generated
```

## Lean Surface

The graph-facing wrapper source is:

```lean
import Circle.Applications.CircleGraphCoverage
```

Stable public import:

```lean
import Circle.Applications.Public
```

Primary declarations:

- `Circle.Applications.circleGraphStrideReach_eq_div_gcd`
- `Circle.Applications.circleGraphStrideFullCoverage_iff_coprime`
- `Circle.Applications.circleGraphLocalWindowCovers_iff_context_sub_one_le`
- `Circle.Applications.circleGraphFamilyCovers_iff_uncoveredLagList_eq_nil`
- `Circle.Applications.circleGraphFamilyCovers_iff_coveredLagList_length_eq_context_sub_one`
- `Circle.Applications.circleGraphCompleteFixture_9_2_2_3_4_7`

The theorem ids are `CC-T0133` through `CC-T0138`. These are graph-facing
wrappers around the existing sparse-attention proof spine in
`Circle.Applications.CircleTransformer`.

## Python: Complete Fixture

```python
from circle_math.ai_contracts import circle_graph_coverage_report

report = circle_graph_coverage_report(
    context=9,
    strides=(3, 4, 7),
    path_length=2,
    local_window=2,
)

print(report.coverage_complete)
print(report.covered_lags)
print(report.uncovered_lags)
print(report.directed_edge_count)
```

Expected output:

```text
True
(1, 2, 3, 6, 4, 8, 7, 5)
()
72
```

The `72` edge count is `9` query vertices times `8` positive lag generators.
The theorem-backed claim is direct positive-lag coverage for this finite graph,
not that this is a good neural architecture.

## Python: Gap Fixture

```python
from circle_math.ai_contracts import circle_graph_coverage_report

report = circle_graph_coverage_report(
    context=120,
    strides=(7, 13),
    path_length=3,
    local_window=4,
)

print(report.coverage_complete)
print(report.first_uncovered_lag)
print(report.uncovered_lag_intervals)
```

Expected shape:

```text
False
5
((5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119))
```

The uncovered intervals are finite gap certificates. They say exactly which
positive lags are missing from this declared graph.

## Python: Edges

```python
from circle_math.ai_contracts import circle_graph_directed_edges

edges = circle_graph_directed_edges(5, (1, 2))
print(edges[:4])
```

Expected output:

```text
((0, 4), (0, 3), (1, 0), (1, 4))
```

This edge list is executable graph data. The formal coverage facts are stated
over lags and uncovered-lag lists, which keeps the proof surface small and
composable.
