import Circle.Basic
import Mathlib.Combinatorics.SimpleGraph.Circulant
import Mathlib.Combinatorics.SimpleGraph.UnitDistance.Basic

namespace Circle

/-- The finite cycle graph is the circulant graph with jump set `{1}`. -/
theorem cycle_graph_circulant_bridge (n : Nat) :
    SimpleGraph.cycleGraph (n + 1) =
      SimpleGraph.circulantGraph ({1} : Set (Fin (n + 1))) := by
  simpa using SimpleGraph.cycleGraph_eq_circulantGraph n

/-- The cycle graph on `n + 1` vertices is connected. -/
theorem cycle_graph_connected_bridge (n : Nat) :
    (SimpleGraph.cycleGraph (n + 1)).Connected := by
  simpa using (SimpleGraph.cycleGraph_connected (n := n))

/-- Any injection of vertices into a metric space is a unit-distance embedding
of the empty graph.
-/
def empty_graph_unit_distance_embedding_bridge
    {V E : Type*} [MetricSpace E] (p : V ↪ E) :
    (⊥ : SimpleGraph V).UnitDistEmbedding E := by
  exact SimpleGraph.UnitDistEmbedding.bot p

end Circle
