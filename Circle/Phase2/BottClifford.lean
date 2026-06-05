/-!
Phase II Bott/Clifford seed.

This module formalizes only the finite period-8 dimension clock used to index
future Bott and Clifford periodicity work. It does not formalize Clifford
algebras, K-theory, or Bott periodicity.
-/

namespace Circle.Phase2

def bottClockIndex (dimension : Nat) : Nat :=
  dimension % 8

theorem bottClockIndex_lt_eight (dimension : Nat) :
    bottClockIndex dimension < 8 := by
  unfold bottClockIndex
  exact Nat.mod_lt dimension (by omega)

theorem bottClockIndex_add_eight (dimension : Nat) :
    bottClockIndex (dimension + 8) = bottClockIndex dimension := by
  unfold bottClockIndex
  omega

theorem bottClockIndex_zero :
    bottClockIndex 0 = 0 := by
  rfl

end Circle.Phase2
