import Circle.Common.Scaffold
import Circle.S3.Scaffold

namespace Circle.S4

def dimension : Nat := 4

def counts (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S3.suspendedSuspendedCircleCounts n)

theorem counts_eq_suspension_s3 (n : Nat) :
    counts n = Circle.Common.suspensionCounts (Circle.S3.suspendedSuspendedCircleCounts n) := by
  rfl

theorem eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (counts n) = 2 := by
  unfold counts
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S3.suspendedSuspendedCircle_chi]
  simp

theorem iteratedSuspensionEulerParity (n : Nat) :
    Circle.Common.eulerCharacteristic (counts n) = 2 ∧
      Circle.Common.eulerCharacteristic (Circle.Common.suspensionCounts (counts n)) = 0 ∧
      Circle.Common.eulerCharacteristic
        (Circle.Common.suspensionCounts (Circle.Common.suspensionCounts (counts n))) = 2 := by
  constructor
  · exact eulerCharacteristic n
  · constructor
    · rw [Circle.Common.suspensionEuler]
      rw [eulerCharacteristic]
      simp
    · rw [Circle.Common.suspensionEuler]
      have h :
          Circle.Common.eulerCharacteristic (Circle.Common.suspensionCounts (counts n)) = 0 := by
        rw [Circle.Common.suspensionEuler]
        rw [eulerCharacteristic]
        simp
      rw [h]
      simp

def quaternionicHopfBaseName : String :=
  "S4-T0001"

end Circle.S4
