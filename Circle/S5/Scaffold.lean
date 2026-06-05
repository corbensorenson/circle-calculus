import Circle.Common.Scaffold
import Circle.S4.Scaffold

namespace Circle.S5

def dimension : Nat := 5

def counts (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S4.counts n)

theorem eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (counts n) = 0 := by
  unfold counts
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S4.eulerCharacteristic]
  simp

def complexProjectiveBridgeName : String :=
  "S5-T0001"

end Circle.S5
