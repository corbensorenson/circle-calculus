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

theorem fourSuspensionCounts_eq_double_double (counts : List Nat) :
    fourSuspensionCounts counts = doubleSuspensionCounts (doubleSuspensionCounts counts) := by
  rfl

theorem fourSuspensionEuler (counts : List Nat) :
    Circle.Common.eulerCharacteristic (fourSuspensionCounts counts) =
      Circle.Common.eulerCharacteristic counts := by
  unfold fourSuspensionCounts
  rw [doubleSuspensionEuler, doubleSuspensionEuler]

def eightSuspensionCounts (counts : List Nat) : List Nat :=
  fourSuspensionCounts (fourSuspensionCounts counts)

theorem eightSuspensionCounts_eq_four_four (counts : List Nat) :
    eightSuspensionCounts counts = fourSuspensionCounts (fourSuspensionCounts counts) := by
  rfl

theorem eightSuspensionEuler (counts : List Nat) :
    Circle.Common.eulerCharacteristic (eightSuspensionCounts counts) =
      Circle.Common.eulerCharacteristic counts := by
  unfold eightSuspensionCounts
  rw [fourSuspensionEuler, fourSuspensionEuler]

end Circle.Phase2
