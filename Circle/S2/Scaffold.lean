import Circle.Common.Scaffold
import Circle.S1.Scaffold

namespace Circle.S2

structure SuspendedCircleSpec where
  modulus : Nat
deriving DecidableEq, Repr

structure SphereGridSpec where
  modulus : Nat
  latitudes : Nat
deriving DecidableEq, Repr

def suspendedCircleCounts (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts [n, n]

theorem suspendedCircle_counts (n : Nat) :
    suspendedCircleCounts n = [n + 2, 3 * n, 2 * n] := by
  simp [suspendedCircleCounts, Circle.Common.suspensionCounts, Circle.Common.suspensionTail]
  omega

theorem suspendedCircle_chi (n : Nat) :
    Circle.Common.eulerCharacteristic (suspendedCircleCounts n) = 2 := by
  rw [suspendedCircle_counts]
  simp [Circle.Common.eulerCharacteristic]
  omega

def sphereGridCounts (n r : Nat) : List Nat :=
  [n * r + 2, n * r + n * (r + 1), n * (r + 1)]

theorem sphereGrid_counts (n r : Nat) :
    sphereGridCounts n r = [n * r + 2, n * r + n * (r + 1), n * (r + 1)] := by
  rfl

theorem sphereGrid_chi (n r : Nat) :
    Circle.Common.eulerCharacteristic (sphereGridCounts n r) = 2 := by
  rw [sphereGrid_counts]
  simp [Circle.Common.eulerCharacteristic]

end Circle.S2
