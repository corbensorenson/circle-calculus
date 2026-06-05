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

end Circle.S2
