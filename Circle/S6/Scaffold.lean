import Circle.Common.Scaffold
import Circle.S5.Scaffold

namespace Circle.S6

def dimension : Nat := 6

def counts (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S5.counts n)

theorem counts_eq_suspension_s5 (n : Nat) :
    counts n = Circle.Common.suspensionCounts (Circle.S5.counts n) := by
  rfl

theorem eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (counts n) = 2 := by
  unfold counts
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S5.eulerCharacteristic]
  simp

def warningLayerName : String :=
  "S6-W0001"

end Circle.S6
