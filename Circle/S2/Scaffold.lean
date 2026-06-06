import Circle.Common.Scaffold
import Circle.S1.Scaffold
import Circle.Core.Rotation
import Circle.Core.Period
import Circle.Core.Orbit

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

def suspendedCircleLongitudeRotation (n : Nat) (stride : Int) : SuspendedCirclePoint n -> SuspendedCirclePoint n
  | SuspendedCirclePoint.north => SuspendedCirclePoint.north
  | SuspendedCirclePoint.south => SuspendedCirclePoint.south
  | SuspendedCirclePoint.equator node => SuspendedCirclePoint.equator (Circle.S1.signedRot n stride node)

def isSuspendedPole {n : Nat} : SuspendedCirclePoint n -> Prop
  | SuspendedCirclePoint.north => True
  | SuspendedCirclePoint.south => True
  | SuspendedCirclePoint.equator _ => False

def isSuspendedEquator {n : Nat} : SuspendedCirclePoint n -> Prop
  | SuspendedCirclePoint.north => False
  | SuspendedCirclePoint.south => False
  | SuspendedCirclePoint.equator _ => True

def suspendedCircleAntipodalPair (n : Nat)
    (p q : SuspendedCirclePoint n) : Prop :=
  suspendedCircleAntipode n p = q

theorem suspendedCircleAntipode_swapsPoles (n : Nat) :
    suspendedCircleAntipode n SuspendedCirclePoint.north = SuspendedCirclePoint.south ∧
      suspendedCircleAntipode n SuspendedCirclePoint.south = SuspendedCirclePoint.north := by
  constructor <;> rfl

theorem suspendedCircleAntipode_involutive (n : Nat) (point : SuspendedCirclePoint n) :
    suspendedCircleAntipode n (suspendedCircleAntipode n point) = point := by
  cases point <;> simp [suspendedCircleAntipode]

theorem suspendedCircleAntipode_bijective (n : Nat) :
    Function.Bijective (suspendedCircleAntipode n) := by
  constructor
  · intro x y h
    calc
      x = suspendedCircleAntipode n (suspendedCircleAntipode n x) :=
        (suspendedCircleAntipode_involutive n x).symm
      _ = suspendedCircleAntipode n (suspendedCircleAntipode n y) := by rw [h]
      _ = y := suspendedCircleAntipode_involutive n y
  · intro y
    exact ⟨suspendedCircleAntipode n y, suspendedCircleAntipode_involutive n y⟩

theorem suspendedCircleLongitudeRotation_bijective (n : Nat) (stride : Int) :
    Function.Bijective (suspendedCircleLongitudeRotation n stride) := by
  constructor
  · intro x y h
    cases x <;> cases y <;> simp [suspendedCircleLongitudeRotation] at h ⊢
    exact (Circle.S1.signedRot_bijective n stride).1 h
  · intro y
    cases y with
    | north =>
        exact ⟨SuspendedCirclePoint.north, rfl⟩
    | south =>
        exact ⟨SuspendedCirclePoint.south, rfl⟩
    | equator node =>
        obtain ⟨pre, hpre⟩ := (Circle.S1.signedRot_bijective n stride).2 node
        exact ⟨SuspendedCirclePoint.equator pre, by
          simp [suspendedCircleLongitudeRotation, hpre]⟩

theorem suspendedCircleAntipode_longitudeRotation_opposite
    (n : Nat) (stride : Int) (point : SuspendedCirclePoint n) :
    suspendedCircleAntipode n (suspendedCircleLongitudeRotation n stride point) =
      suspendedCircleLongitudeRotation n (-stride) (suspendedCircleAntipode n point) := by
  cases point <;>
    simp [suspendedCircleAntipode, suspendedCircleLongitudeRotation, Circle.S1.signedRot, add_comm]

theorem suspendedCircleAntipode_preservesPoleSet (n : Nat)
    (point : SuspendedCirclePoint n) :
    isSuspendedPole (suspendedCircleAntipode n point) ↔ isSuspendedPole point := by
  cases point <;> simp [isSuspendedPole, suspendedCircleAntipode]

theorem suspendedCircleAntipode_preservesEquatorSet (n : Nat)
    (point : SuspendedCirclePoint n) :
    isSuspendedEquator (suspendedCircleAntipode n point) ↔ isSuspendedEquator point := by
  cases point <;> simp [isSuspendedEquator, suspendedCircleAntipode]

theorem suspendedCircleAntipodalPair_self_antipode (n : Nat)
    (point : SuspendedCirclePoint n) :
    suspendedCircleAntipodalPair n point (suspendedCircleAntipode n point) := by
  rfl

theorem suspendedCircleAntipodalPair_symmetric (n : Nat)
    (p q : SuspendedCirclePoint n) :
    suspendedCircleAntipodalPair n p q ↔ suspendedCircleAntipodalPair n q p := by
  unfold suspendedCircleAntipodalPair
  constructor
  · intro hpq
    rw [← hpq]
    exact suspendedCircleAntipode_involutive n p
  · intro hqp
    rw [← hqp]
    exact suspendedCircleAntipode_involutive n q

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

def sphereGridLatitudeCoordinate {n r : Nat} : SphereGridPoint n r -> Option (Fin r)
  | SphereGridPoint.north => none
  | SphereGridPoint.south => none
  | SphereGridPoint.ring latitude _ => some latitude

def sphereGridLongitudeCoordinate {n r : Nat} : SphereGridPoint n r -> Option (Circle.C n)
  | SphereGridPoint.north => none
  | SphereGridPoint.south => none
  | SphereGridPoint.ring _ node => some node

theorem longitudeRotation_fixesPoles (n r stride : Nat) :
    longitudeRotation n r stride SphereGridPoint.north = SphereGridPoint.north ∧
      longitudeRotation n r stride SphereGridPoint.south = SphereGridPoint.south := by
  constructor <;> rfl

theorem longitudeRotation_preservesLatitudeCoordinate (n r stride : Nat)
    (point : SphereGridPoint n r) :
    sphereGridLatitudeCoordinate (longitudeRotation n r stride point) =
      sphereGridLatitudeCoordinate point := by
  cases point <;> rfl

theorem longitudeRotation_advancesLongitudeCoordinate (n r stride : Nat)
    (point : SphereGridPoint n r) :
    sphereGridLongitudeCoordinate (longitudeRotation n r stride point) =
      (sphereGridLongitudeCoordinate point).map (Circle.rot n stride) := by
  cases point <;> rfl

theorem latitudeCoil_period {n k : Nat} (hn : n ≠ 0) :
    Circle.period n k = n / Nat.gcd n k :=
  Circle.period_eq_n_div_gcd hn

noncomputable def latitudeRingOrbitClassCount (n k r : Nat) (_latitude : Fin r) : Nat :=
  Circle.orbitClassCount n k

theorem latitudeRingOrbitClassCount_eq_gcd {n k r : Nat}
    (latitude : Fin r) (hn : n ≠ 0) :
    latitudeRingOrbitClassCount n k r latitude = Nat.gcd n k :=
  Circle.orbit_decomposition_count hn

end Circle.S2
