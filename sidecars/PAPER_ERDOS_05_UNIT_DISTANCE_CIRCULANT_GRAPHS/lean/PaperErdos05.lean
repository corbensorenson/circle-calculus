import Circle.Erdos.GraphLab

namespace PaperErdos05

/-- Paper-sidecar access to the cycle-as-circulant bridge. -/
theorem cycle_graph_circulant_bridge (n : Nat) :
    SimpleGraph.cycleGraph (n + 1) =
      SimpleGraph.circulantGraph ({1} : Set (Fin (n + 1))) :=
  Circle.cycle_graph_circulant_bridge n

/-- Paper-sidecar access to cycle-graph connectedness. -/
theorem cycle_graph_connected_bridge (n : Nat) :
    (SimpleGraph.cycleGraph (n + 1)).Connected :=
  Circle.cycle_graph_connected_bridge n

/-- Paper-sidecar access to the empty-graph unit-distance embedding constructor. -/
def empty_graph_unit_distance_embedding_bridge
    {V E : Type*} [MetricSpace E] (p : V ↪ E) :
    (⊥ : SimpleGraph V).UnitDistEmbedding E :=
  Circle.empty_graph_unit_distance_embedding_bridge p

end PaperErdos05
