import Circle.Common.Scaffold
import Circle.S6.Scaffold

namespace Circle.S7

def dimension : Nat := 7

def iteratedSuspensionModel (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S6.counts n)

theorem eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (iteratedSuspensionModel n) = 0 := by
  unfold iteratedSuspensionModel
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S6.eulerCharacteristic]
  simp

def octonionTrackName : String :=
  "S7O"

end Circle.S7
