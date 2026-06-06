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

theorem unitQuaternion_ext {p q : UnitQuaternion} (h : p.val = q.val) : p = q := by
  cases p
  cases q
  simp at h
  subst h
  simp

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

noncomputable def unitQuaternionOne : UnitQuaternion where
  val := 1
  unit := by
    unfold quaternionNorm
    simp

noncomputable def unitQuaternionConj (q : UnitQuaternion) : UnitQuaternion where
  val := star q.val
  unit := by
    rw [quaternionNorm, Quaternion.normSq_star]
    exact q.unit

noncomputable def unitQuaternionNeg (q : UnitQuaternion) : UnitQuaternion where
  val := -q.val
  unit := by
    rw [quaternionNorm, Quaternion.normSq_neg]
    exact q.unit

theorem unitQuaternion_one_mul (q : UnitQuaternion) :
    unitQuaternionMul unitQuaternionOne q = q := by
  cases q
  simp [unitQuaternionMul, unitQuaternionOne]

theorem unitQuaternion_mul_one (q : UnitQuaternion) :
    unitQuaternionMul q unitQuaternionOne = q := by
  cases q
  simp [unitQuaternionMul, unitQuaternionOne]

theorem unitQuaternion_identity (q : UnitQuaternion) :
    unitQuaternionMul unitQuaternionOne q = q ∧
      unitQuaternionMul q unitQuaternionOne = q := by
  exact ⟨unitQuaternion_one_mul q, unitQuaternion_mul_one q⟩

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

theorem unitQuaternion_mul_conj (q : UnitQuaternion) :
    unitQuaternionMul q (unitQuaternionConj q) = unitQuaternionOne := by
  apply unitQuaternion_ext
  exact (unitQuaternion_inverse q).1

theorem unitQuaternion_conj_mul (q : UnitQuaternion) :
    unitQuaternionMul (unitQuaternionConj q) q = unitQuaternionOne := by
  apply unitQuaternion_ext
  exact (unitQuaternion_inverse q).2

theorem unitQuaternion_conj_inverse (q : UnitQuaternion) :
    unitQuaternionMul q (unitQuaternionConj q) = unitQuaternionOne ∧
      unitQuaternionMul (unitQuaternionConj q) q = unitQuaternionOne := by
  exact ⟨unitQuaternion_mul_conj q, unitQuaternion_conj_mul q⟩

theorem unitQuaternion_neg_involutive (q : UnitQuaternion) :
    unitQuaternionNeg (unitQuaternionNeg q) = q := by
  apply unitQuaternion_ext
  simp [unitQuaternionNeg]

def spinSignRelated (p q : UnitQuaternion) : Prop :=
  q = p ∨ q = unitQuaternionNeg p

theorem spinSignRelated_refl (q : UnitQuaternion) :
    spinSignRelated q q := by
  left
  rfl

theorem spinSignRelated_symm {p q : UnitQuaternion}
    (h : spinSignRelated p q) :
    spinSignRelated q p := by
  cases h with
  | inl hqp =>
      left
      exact hqp.symm
  | inr hqneg =>
      right
      rw [hqneg]
      exact (unitQuaternion_neg_involutive p).symm

theorem spinSignRelated_trans {p q r : UnitQuaternion}
    (hpq : spinSignRelated p q) (hqr : spinSignRelated q r) :
    spinSignRelated p r := by
  cases hpq with
  | inl hqp =>
      rw [hqp] at hqr
      exact hqr
  | inr hqneg =>
      cases hqr with
      | inl hrq =>
          right
          rw [hrq, hqneg]
      | inr hrneg =>
          left
          rw [hrneg, hqneg, unitQuaternion_neg_involutive]

theorem spinSignRelated_equivalence :
    Equivalence spinSignRelated := by
  exact ⟨spinSignRelated_refl, spinSignRelated_symm, spinSignRelated_trans⟩

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

noncomputable def quaternionConjugationAction (q v : RealQuaternion) : RealQuaternion :=
  q * v * star q

theorem quaternionConjugation_one (v : RealQuaternion) :
    quaternionConjugationAction 1 v = v := by
  simp [quaternionConjugationAction]

theorem quaternionConjugation_zero_vector (q : RealQuaternion) :
    quaternionConjugationAction q 0 = 0 := by
  simp [quaternionConjugationAction]

theorem quaternionConjugation_neg (q v : RealQuaternion) :
    quaternionConjugationAction (-q) v = quaternionConjugationAction q v := by
  ext <;> simp [quaternionConjugationAction] <;> ring

structure HopfPair where
  z0re : ℝ
  z0im : ℝ
  z1re : ℝ
  z1im : ℝ

structure HopfBasePoint where
  x : ℝ
  y : ℝ
  z : ℝ

theorem hopfBasePoint_ext {p q : HopfBasePoint}
    (hx : p.x = q.x) (hy : p.y = q.y) (hz : p.z = q.z) : p = q := by
  cases p
  cases q
  simp at hx hy hz
  simp [hx, hy, hz]

def hopfPairNormSq (p : HopfPair) : ℝ :=
  p.z0re * p.z0re + p.z0im * p.z0im + p.z1re * p.z1re + p.z1im * p.z1im

def hopfBaseNormSq (p : HopfBasePoint) : ℝ :=
  p.x * p.x + p.y * p.y + p.z * p.z

def hopfMap (p : HopfPair) : HopfBasePoint where
  x := 2 * (p.z0re * p.z1re + p.z0im * p.z1im)
  y := 2 * (p.z0im * p.z1re - p.z0re * p.z1im)
  z := p.z0re * p.z0re + p.z0im * p.z0im - (p.z1re * p.z1re + p.z1im * p.z1im)

theorem hopfBaseNormSq_hopfMap (p : HopfPair) :
    hopfBaseNormSq (hopfMap p) = hopfPairNormSq p * hopfPairNormSq p := by
  cases p
  simp [hopfBaseNormSq, hopfMap, hopfPairNormSq]
  ring

theorem hopfMap_lands_sphere (p : HopfPair) (h : hopfPairNormSq p = 1) :
    hopfBaseNormSq (hopfMap p) = 1 := by
  rw [hopfBaseNormSq_hopfMap, h]
  ring

def phaseRotatePair (u v : ℝ) (p : HopfPair) : HopfPair where
  z0re := u * p.z0re - v * p.z0im
  z0im := v * p.z0re + u * p.z0im
  z1re := u * p.z1re - v * p.z1im
  z1im := v * p.z1re + u * p.z1im

structure HopfPhase where
  re : ℝ
  im : ℝ

def hopfPhaseIdentity : HopfPhase where
  re := 1
  im := 0

def hopfPhaseMul (left right : HopfPhase) : HopfPhase where
  re := left.re * right.re - left.im * right.im
  im := left.im * right.re + left.re * right.im

def hopfPhaseAct (phase : HopfPhase) (p : HopfPair) : HopfPair :=
  phaseRotatePair phase.re phase.im p

theorem phaseRotatePair_identity (p : HopfPair) :
    phaseRotatePair 1 0 p = p := by
  cases p
  simp [phaseRotatePair]

theorem phaseRotatePair_comp (u v a b : ℝ) (p : HopfPair) :
    phaseRotatePair u v (phaseRotatePair a b p) =
      phaseRotatePair (u * a - v * b) (v * a + u * b) p := by
  cases p
  simp [phaseRotatePair]
  constructor
  · ring
  constructor
  · ring
  constructor
  · ring
  · ring

theorem hopfPhaseAct_identity (p : HopfPair) :
    hopfPhaseAct hopfPhaseIdentity p = p :=
  phaseRotatePair_identity p

theorem hopfPhaseAct_comp (left right : HopfPhase) (p : HopfPair) :
    hopfPhaseAct left (hopfPhaseAct right p) =
      hopfPhaseAct (hopfPhaseMul left right) p :=
  phaseRotatePair_comp left.re left.im right.re right.im p

theorem hopfPhaseAction_laws (left right : HopfPhase) (p : HopfPair) :
    hopfPhaseAct hopfPhaseIdentity p = p ∧
      hopfPhaseAct left (hopfPhaseAct right p) =
        hopfPhaseAct (hopfPhaseMul left right) p := by
  exact ⟨hopfPhaseAct_identity p, hopfPhaseAct_comp left right p⟩

theorem phaseRotatePair_norm_sq (u v : ℝ) (p : HopfPair) :
    hopfPairNormSq (phaseRotatePair u v p) =
      (u * u + v * v) * hopfPairNormSq p := by
  cases p
  simp [hopfPairNormSq, phaseRotatePair]
  ring

theorem hopfMap_phase_invariant (u v : ℝ) (huv : u * u + v * v = 1) (p : HopfPair) :
    hopfMap (phaseRotatePair u v p) = hopfMap p := by
  have huv_sq : u ^ 2 + v ^ 2 = 1 := by nlinarith [huv]
  rcases p with ⟨a, b, c, d⟩
  apply hopfBasePoint_ext
  · simp [hopfMap, phaseRotatePair]
    calc
      (u * a - v * b) * (u * c - v * d) + (v * a + u * b) * (v * c + u * d) =
          (u ^ 2 + v ^ 2) * (a * c + b * d) := by ring
      _ = a * c + b * d := by rw [huv_sq]; ring
  · simp [hopfMap, phaseRotatePair]
    calc
      (v * a + u * b) * (u * c - v * d) - (u * a - v * b) * (v * c + u * d) =
          (u ^ 2 + v ^ 2) * (b * c - a * d) := by ring
      _ = b * c - a * d := by rw [huv_sq]; ring
  · simp [hopfMap, phaseRotatePair]
    calc
      (u * a - v * b) * (u * a - v * b) + (v * a + u * b) * (v * a + u * b) -
          ((u * c - v * d) * (u * c - v * d) + (v * c + u * d) * (v * c + u * d)) =
          (u ^ 2 + v ^ 2) * (a * a + b * b) -
            (u ^ 2 + v ^ 2) * (c * c + d * d) := by ring
      _ = a * a + b * b - (c * c + d * d) := by rw [huv_sq]; ring

theorem hopfFiber_circle_like (u v : ℝ) (huv : u * u + v * v = 1)
    (p : HopfPair) (hp : hopfPairNormSq p = 1) :
    hopfPairNormSq (phaseRotatePair u v p) = 1 ∧
      hopfMap (phaseRotatePair u v p) = hopfMap p := by
  constructor
  · rw [phaseRotatePair_norm_sq, huv, hp]
    ring
  · exact hopfMap_phase_invariant u v huv p

def quaternionTrackName : String :=
  "S3Q"

def hopfTrackName : String :=
  "S3H"

end Circle.S3
