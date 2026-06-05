import Circle.Common.Scaffold

/-!
Phase II stable-sphere seed.

This module keeps the first stable-sphere claims inside the finite
cell-count model already used by the dimensional ladder. It does not claim a
formal spectrum model.
-/

namespace Circle.Phase2

def doubleSuspensionCounts (counts : List Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.Common.suspensionCounts counts)

theorem doubleSuspensionEuler (counts : List Nat) :
    Circle.Common.eulerCharacteristic (doubleSuspensionCounts counts) =
      Circle.Common.eulerCharacteristic counts := by
  unfold doubleSuspensionCounts
  rw [Circle.Common.suspensionEuler, Circle.Common.suspensionEuler]
  omega

def fourSuspensionCounts (counts : List Nat) : List Nat :=
  doubleSuspensionCounts (doubleSuspensionCounts counts)

theorem fourSuspensionEuler (counts : List Nat) :
    Circle.Common.eulerCharacteristic (fourSuspensionCounts counts) =
      Circle.Common.eulerCharacteristic counts := by
  unfold fourSuspensionCounts
  rw [doubleSuspensionEuler, doubleSuspensionEuler]

end Circle.Phase2
