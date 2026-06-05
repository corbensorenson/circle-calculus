import Mathlib.Algebra.Quaternion
import Mathlib.Data.Real.Basic
import Circle.Common.Scaffold
import Circle.S2.Scaffold

namespace Circle.S3

abbrev RealQuaternion :=
  Quaternion ℝ

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

def quaternionNorm (q : RealQuaternion) : ℝ :=
  Quaternion.normSq q

structure UnitQuaternion where
  val : RealQuaternion
  unit : quaternionNorm val = 1

theorem unitQuaternion_mul_closed (p q : UnitQuaternion) :
    quaternionNorm (p.val * q.val) = 1 := by
  unfold quaternionNorm
  rw [map_mul]
  change quaternionNorm p.val * quaternionNorm q.val = 1
  rw [p.unit, q.unit]
  simp

noncomputable def unitQuaternionMul (p q : UnitQuaternion) : UnitQuaternion where
  val := p.val * q.val
  unit := unitQuaternion_mul_closed p q

theorem unitQuaternion_inverse (q : UnitQuaternion) :
    q.val * star q.val = 1 ∧ star q.val * q.val = 1 := by
  constructor
  · rw [Quaternion.self_mul_star]
    change ((quaternionNorm q.val : ℝ) : RealQuaternion) = 1
    rw [q.unit]
    rfl
  · rw [Quaternion.star_mul_self]
    change ((quaternionNorm q.val : ℝ) : RealQuaternion) = 1
    rw [q.unit]
    rfl

def quaternionI : Quaternion ℤ :=
  ⟨0, 1, 0, 0⟩

def quaternionJ : Quaternion ℤ :=
  ⟨0, 0, 1, 0⟩

theorem quaternion_noncommutative_example :
    quaternionI * quaternionJ ≠ quaternionJ * quaternionI := by
  intro h
  have hk := congrArg (fun q : Quaternion ℤ => q.imK) h
  simp [quaternionI, quaternionJ] at hk

theorem quaternion_mul_assoc (a b c : RealQuaternion) :
    (a * b) * c = a * (b * c) :=
  mul_assoc a b c

def quaternionTrackName : String :=
  "S3Q"

def hopfTrackName : String :=
  "S3H"

end Circle.S3
