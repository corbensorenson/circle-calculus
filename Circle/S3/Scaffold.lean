import Circle.Common.Scaffold
import Circle.S2.Scaffold

namespace Circle.S3

structure SuspendedSurfaceSpec where
  vertices : Nat
  edges : Nat
  faces : Nat
deriving DecidableEq, Repr

def suspensionSurfaceCounts (vertices edges faces : Nat) : List Nat :=
  Circle.Common.suspensionCounts [vertices, edges, faces]

theorem suspensionSurface_counts (vertices edges faces : Nat) :
    suspensionSurfaceCounts vertices edges faces =
      [vertices + 2, edges + 2 * vertices, faces + 2 * edges, 2 * faces] := by
  simp [suspensionSurfaceCounts, Circle.Common.suspensionCounts, Circle.Common.suspensionTail]

theorem suspensionSurface_chi_zero (vertices edges faces : Nat)
    (hchi : Circle.Common.eulerCharacteristic [vertices, edges, faces] = 2) :
    Circle.Common.eulerCharacteristic (suspensionSurfaceCounts vertices edges faces) = 0 := by
  unfold suspensionSurfaceCounts
  rw [Circle.Common.suspensionEuler]
  rw [hchi]
  simp

def suspendedSuspendedCircleCounts (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S2.suspendedCircleCounts n)

theorem suspendedSuspendedCircle_counts (n : Nat) :
    suspendedSuspendedCircleCounts n = [n + 4, 5 * n + 4, 8 * n, 4 * n] := by
  unfold suspendedSuspendedCircleCounts
  rw [Circle.S2.suspendedCircle_counts]
  simp [Circle.Common.suspensionCounts, Circle.Common.suspensionTail]
  omega

theorem suspendedSuspendedCircle_chi (n : Nat) :
    Circle.Common.eulerCharacteristic (suspendedSuspendedCircleCounts n) = 0 := by
  unfold suspendedSuspendedCircleCounts
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S2.suspendedCircle_chi]
  simp

def quaternionTrackName : String :=
  "S3Q"

def hopfTrackName : String :=
  "S3H"

end Circle.S3
