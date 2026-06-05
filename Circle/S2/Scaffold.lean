import Circle.Common.Scaffold
import Circle.S1.Scaffold
import Circle.Core.Rotation
import Circle.Core.Period

namespace Circle.S2

structure SuspendedCircleSpec where
  modulus : Nat
deriving DecidableEq, Repr

structure SphereGridSpec where
  modulus : Nat
  latitudes : Nat
deriving DecidableEq, Repr

inductive SuspendedCirclePoint (n : Nat)
  | north
  | south
  | equator (node : Circle.C n)
deriving DecidableEq

def suspendedCircleAntipode (n : Nat) : SuspendedCirclePoint n -> SuspendedCirclePoint n
  | SuspendedCirclePoint.north => SuspendedCirclePoint.south
  | SuspendedCirclePoint.south => SuspendedCirclePoint.north
  | SuspendedCirclePoint.equator node => SuspendedCirclePoint.equator (-node)

def isSuspendedPole {n : Nat} : SuspendedCirclePoint n -> Prop
  | SuspendedCirclePoint.north => True
  | SuspendedCirclePoint.south => True
  | SuspendedCirclePoint.equator _ => False

def isSuspendedEquator {n : Nat} : SuspendedCirclePoint n -> Prop
  | SuspendedCirclePoint.north => False
  | SuspendedCirclePoint.south => False
  | SuspendedCirclePoint.equator _ => True

theorem suspendedCircleAntipode_swapsPoles (n : Nat) :
    suspendedCircleAntipode n SuspendedCirclePoint.north = SuspendedCirclePoint.south ∧
      suspendedCircleAntipode n SuspendedCirclePoint.south = SuspendedCirclePoint.north := by
  constructor <;> rfl

theorem suspendedCircleAntipode_involutive (n : Nat) (point : SuspendedCirclePoint n) :
    suspendedCircleAntipode n (suspendedCircleAntipode n point) = point := by
  cases point <;> simp [suspendedCircleAntipode]

theorem suspendedCircleAntipode_preservesPoleSet (n : Nat)
    (point : SuspendedCirclePoint n) :
    isSuspendedPole (suspendedCircleAntipode n point) ↔ isSuspendedPole point := by
  cases point <;> simp [isSuspendedPole, suspendedCircleAntipode]

theorem suspendedCircleAntipode_preservesEquatorSet (n : Nat)
    (point : SuspendedCirclePoint n) :
    isSuspendedEquator (suspendedCircleAntipode n point) ↔ isSuspendedEquator point := by
  cases point <;> simp [isSuspendedEquator, suspendedCircleAntipode]

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

abbrev LatitudeRing (n r : Nat) (_latitude : Fin r) :=
  Circle.C n

theorem latitudeRing_isCircle (n r : Nat) (latitude : Fin r) :
    LatitudeRing n r latitude = Circle.C n := by
  rfl

inductive SphereGridPoint (n r : Nat)
  | north
  | south
  | ring (latitude : Fin r) (node : Circle.C n)

def longitudeRotation (n r stride : Nat) : SphereGridPoint n r -> SphereGridPoint n r
  | SphereGridPoint.north => SphereGridPoint.north
  | SphereGridPoint.south => SphereGridPoint.south
  | SphereGridPoint.ring latitude node => SphereGridPoint.ring latitude (Circle.rot n stride node)

theorem longitudeRotation_fixesPoles (n r stride : Nat) :
    longitudeRotation n r stride SphereGridPoint.north = SphereGridPoint.north ∧
      longitudeRotation n r stride SphereGridPoint.south = SphereGridPoint.south := by
  constructor <;> rfl

theorem latitudeCoil_period {n k : Nat} (hn : n ≠ 0) :
    Circle.period n k = n / Nat.gcd n k :=
  Circle.period_eq_n_div_gcd hn

end Circle.S2
