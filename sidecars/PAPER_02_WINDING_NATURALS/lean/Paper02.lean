import Circle.Basic

/-!
Paper 2 sidecar.

This file re-exports the v0 lifted-winding declarations used by the paper.
The canonical theorem ids live in `manifests/theorem_manifest.yaml`.
-/

namespace Circle.Paper02

#check Circle.LiftedNode
#check Circle.LiftedNode.value
#check Circle.liftWinding
#check Circle.liftResidue
#check Circle.lift_decomposition
#check Circle.lift_residue_lt
#check Circle.lift_exists
#check Circle.lift_unique
#check Circle.liftSuccCarry
#check Circle.liftSuccWinding
#check Circle.liftSuccResidue
#check Circle.lift_successor_decomposition
#check Circle.liftAddCarry
#check Circle.liftAddWinding
#check Circle.liftAddResidue
#check Circle.lift_add_decomposition
#check Circle.lift_add_zero_right
#check Circle.lift_add_zero_left
#check Circle.lift_add_assoc_value
#check Circle.liftSuccPair
#check Circle.liftIterSuccPair
#check Circle.lift_succ_pair_decomposition
#check Circle.lift_iter_successor_decomposition

end Circle.Paper02
