import Circle.Common.Scaffold
import Circle.S6.Scaffold

namespace Circle.S7

def dimension : Nat := 7

def iteratedSuspensionModel (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S6.counts n)

theorem iteratedSuspensionModel_eq_suspension_s6 (n : Nat) :
    iteratedSuspensionModel n = Circle.Common.suspensionCounts (Circle.S6.counts n) := by
  rfl

theorem eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (iteratedSuspensionModel n) = 0 := by
  unfold iteratedSuspensionModel
  rw [Circle.Common.suspensionEuler]
  rw [Circle.S6.eulerCharacteristic]
  simp

structure QuaternionCoord where
  r : ℝ
  i : ℝ
  j : ℝ
  k : ℝ

theorem quaternionCoord_ext {a b : QuaternionCoord}
    (hr : a.r = b.r) (hi : a.i = b.i) (hj : a.j = b.j) (hk : a.k = b.k) :
    a = b := by
  cases a
  cases b
  simp at hr hi hj hk
  simp [hr, hi, hj, hk]

structure QuaternionPair where
  q0 : QuaternionCoord
  q1 : QuaternionCoord

structure HopfBase5 where
  x0 : ℝ
  x1 : ℝ
  x2 : ℝ
  x3 : ℝ
  x4 : ℝ

theorem hopfBase5_ext {p q : HopfBase5}
    (h0 : p.x0 = q.x0) (h1 : p.x1 = q.x1) (h2 : p.x2 = q.x2)
    (h3 : p.x3 = q.x3) (h4 : p.x4 = q.x4) : p = q := by
  cases p
  cases q
  simp at h0 h1 h2 h3 h4
  simp [h0, h1, h2, h3, h4]

def quaternionCoordNormSq (q : QuaternionCoord) : ℝ :=
  q.r * q.r + q.i * q.i + q.j * q.j + q.k * q.k

def quaternionConjCoord (q : QuaternionCoord) : QuaternionCoord where
  r := q.r
  i := -q.i
  j := -q.j
  k := -q.k

def quaternionMulCoord (a b : QuaternionCoord) : QuaternionCoord where
  r := a.r * b.r - a.i * b.i - a.j * b.j - a.k * b.k
  i := a.r * b.i + a.i * b.r + a.j * b.k - a.k * b.j
  j := a.r * b.j - a.i * b.k + a.j * b.r + a.k * b.i
  k := a.r * b.k + a.i * b.j - a.j * b.i + a.k * b.r

def quaternionPairNormSq (p : QuaternionPair) : ℝ :=
  quaternionCoordNormSq p.q0 + quaternionCoordNormSq p.q1

def quaternionPairRightPhase (p : QuaternionPair) (u : QuaternionCoord) : QuaternionPair where
  q0 := quaternionMulCoord p.q0 u
  q1 := quaternionMulCoord p.q1 u

def hopfBase5NormSq (p : HopfBase5) : ℝ :=
  p.x0 * p.x0 + p.x1 * p.x1 + p.x2 * p.x2 + p.x3 * p.x3 + p.x4 * p.x4

def hopfBase5Scale (s : ℝ) (p : HopfBase5) : HopfBase5 where
  x0 := s * p.x0
  x1 := s * p.x1
  x2 := s * p.x2
  x3 := s * p.x3
  x4 := s * p.x4

def quaternionicHopfMap (p : QuaternionPair) : HopfBase5 :=
  let product := quaternionMulCoord p.q0 (quaternionConjCoord p.q1)
  { x0 := 2 * product.r
    x1 := 2 * product.i
    x2 := 2 * product.j
    x3 := 2 * product.k
    x4 := quaternionCoordNormSq p.q0 - quaternionCoordNormSq p.q1 }

theorem quaternionCoordNormSq_mul (a b : QuaternionCoord) :
    quaternionCoordNormSq (quaternionMulCoord a b) =
      quaternionCoordNormSq a * quaternionCoordNormSq b := by
  rcases a with ⟨ar, ai, aj, ak⟩
  rcases b with ⟨br, bi, bj, bk⟩
  simp [quaternionCoordNormSq, quaternionMulCoord]
  ring

theorem quaternionCoordNormSq_conj (q : QuaternionCoord) :
    quaternionCoordNormSq (quaternionConjCoord q) = quaternionCoordNormSq q := by
  rcases q with ⟨r, i, j, k⟩
  simp [quaternionCoordNormSq, quaternionConjCoord]

theorem quaternionMulCoord_assoc (a b c : QuaternionCoord) :
    quaternionMulCoord (quaternionMulCoord a b) c =
      quaternionMulCoord a (quaternionMulCoord b c) := by
  rcases a with ⟨ar, ai, aj, ak⟩
  rcases b with ⟨br, bi, bj, bk⟩
  rcases c with ⟨cr, ci, cj, ck⟩
  apply quaternionCoord_ext <;> simp [quaternionMulCoord] <;> ring

theorem quaternionPairRightPhase_comp
    (p : QuaternionPair) (u v : QuaternionCoord) :
    quaternionPairRightPhase (quaternionPairRightPhase p u) v =
      quaternionPairRightPhase p (quaternionMulCoord u v) := by
  rcases p with ⟨q0, q1⟩
  simp [quaternionPairRightPhase, quaternionMulCoord_assoc]

theorem quaternionicHopfBaseNormSq_hopfMap (p : QuaternionPair) :
    hopfBase5NormSq (quaternionicHopfMap p) =
      quaternionPairNormSq p * quaternionPairNormSq p := by
  rcases p with ⟨⟨a, b, c, d⟩, ⟨e, f, g, h⟩⟩
  simp [hopfBase5NormSq, quaternionicHopfMap, quaternionPairNormSq,
    quaternionCoordNormSq, quaternionConjCoord, quaternionMulCoord]
  ring

theorem quaternionicHopf_lands_sphere (p : QuaternionPair)
    (h : quaternionPairNormSq p = 1) :
    hopfBase5NormSq (quaternionicHopfMap p) = 1 := by
  rw [quaternionicHopfBaseNormSq_hopfMap, h]
  ring

theorem quaternionicHopfMap_rightPhase_scaled (p : QuaternionPair) (u : QuaternionCoord) :
    quaternionicHopfMap (quaternionPairRightPhase p u) =
      hopfBase5Scale (quaternionCoordNormSq u) (quaternionicHopfMap p) := by
  rcases p with ⟨⟨a, b, c, d⟩, ⟨e, f, g, h⟩⟩
  rcases u with ⟨ur, ui, uj, uk⟩
  apply hopfBase5_ext <;>
    simp [quaternionicHopfMap, quaternionPairRightPhase, hopfBase5Scale,
      quaternionCoordNormSq, quaternionConjCoord, quaternionMulCoord] <;>
    ring

theorem quaternionicPhaseInvariance (p : QuaternionPair) (u : QuaternionCoord)
    (hu : quaternionCoordNormSq u = 1) :
    quaternionicHopfMap (quaternionPairRightPhase p u) = quaternionicHopfMap p := by
  rw [quaternionicHopfMap_rightPhase_scaled, hu]
  rcases quaternionicHopfMap p with ⟨x0, x1, x2, x3, x4⟩
  simp [hopfBase5Scale]

theorem quaternionicRightPhaseAction_laws
    (p : QuaternionPair) (u v : QuaternionCoord)
    (hu : quaternionCoordNormSq u = 1) (hv : quaternionCoordNormSq v = 1) :
    quaternionPairRightPhase (quaternionPairRightPhase p u) v =
        quaternionPairRightPhase p (quaternionMulCoord u v) ∧
      quaternionicHopfMap (quaternionPairRightPhase p u) = quaternionicHopfMap p ∧
      quaternionicHopfMap (quaternionPairRightPhase p (quaternionMulCoord u v)) =
        quaternionicHopfMap p := by
  constructor
  · exact quaternionPairRightPhase_comp p u v
  · constructor
    · exact quaternionicPhaseInvariance p u hu
    · apply quaternionicPhaseInvariance
      rw [quaternionCoordNormSq_mul, hu, hv]
      ring

def quaternionAddCoord (a b : QuaternionCoord) : QuaternionCoord where
  r := a.r + b.r
  i := a.i + b.i
  j := a.j + b.j
  k := a.k + b.k

def quaternionNegCoord (a : QuaternionCoord) : QuaternionCoord where
  r := -a.r
  i := -a.i
  j := -a.j
  k := -a.k

def quaternionSubCoord (a b : QuaternionCoord) : QuaternionCoord :=
  quaternionAddCoord a (quaternionNegCoord b)

structure OctonionCoord where
  left : QuaternionCoord
  right : QuaternionCoord

def octonionCoordNormSq (o : OctonionCoord) : ℝ :=
  quaternionCoordNormSq o.left + quaternionCoordNormSq o.right

def octonionConjCoord (o : OctonionCoord) : OctonionCoord where
  left := quaternionConjCoord o.left
  right := quaternionNegCoord o.right

def octonionRealCoord (s : ℝ) : OctonionCoord where
  left := { r := s, i := 0, j := 0, k := 0 }
  right := { r := 0, i := 0, j := 0, k := 0 }

def octonionMulCoord (a b : OctonionCoord) : OctonionCoord where
  left :=
    quaternionSubCoord
      (quaternionMulCoord a.left b.left)
      (quaternionMulCoord (quaternionConjCoord b.right) a.right)
  right :=
    quaternionAddCoord
      (quaternionMulCoord b.right a.left)
      (quaternionMulCoord a.right (quaternionConjCoord b.left))

def octonionBasisCoord (idx : Fin 8) : OctonionCoord :=
  match idx.val with
  | 0 => octonionRealCoord 1
  | 1 => { left := { r := 0, i := 1, j := 0, k := 0 }, right := { r := 0, i := 0, j := 0, k := 0 } }
  | 2 => { left := { r := 0, i := 0, j := 1, k := 0 }, right := { r := 0, i := 0, j := 0, k := 0 } }
  | 3 => { left := { r := 0, i := 0, j := 0, k := 1 }, right := { r := 0, i := 0, j := 0, k := 0 } }
  | 4 => { left := { r := 0, i := 0, j := 0, k := 0 }, right := { r := 1, i := 0, j := 0, k := 0 } }
  | 5 => { left := { r := 0, i := 0, j := 0, k := 0 }, right := { r := 0, i := 1, j := 0, k := 0 } }
  | 6 => { left := { r := 0, i := 0, j := 0, k := 0 }, right := { r := 0, i := 0, j := 1, k := 0 } }
  | _ => { left := { r := 0, i := 0, j := 0, k := 0 }, right := { r := 0, i := 0, j := 0, k := 1 } }

theorem octonionBasis (idx : Fin 8) :
    octonionCoordNormSq (octonionBasisCoord idx) = 1 := by
  fin_cases idx <;> norm_num [octonionBasisCoord, octonionCoordNormSq,
    quaternionCoordNormSq, octonionRealCoord]

theorem octonionConjugateNorm (o : OctonionCoord) :
    octonionMulCoord o (octonionConjCoord o) = octonionRealCoord (octonionCoordNormSq o) := by
  rcases o with ⟨⟨a, b, c, d⟩, ⟨e, f, g, h⟩⟩
  simp [octonionMulCoord, octonionConjCoord, octonionRealCoord, octonionCoordNormSq,
    quaternionCoordNormSq, quaternionConjCoord, quaternionMulCoord, quaternionAddCoord,
    quaternionNegCoord, quaternionSubCoord]
  ring_nf
  tauto

theorem octonionNormMul (a b : OctonionCoord) :
    octonionCoordNormSq (octonionMulCoord a b) =
      octonionCoordNormSq a * octonionCoordNormSq b := by
  rcases a with ⟨⟨ar, ai, aj, ak⟩, ⟨br, bi, bj, bk⟩⟩
  rcases b with ⟨⟨cr, ci, cj, ck⟩, ⟨dr, di, dj, dk⟩⟩
  simp [octonionMulCoord, octonionCoordNormSq, quaternionCoordNormSq,
    quaternionConjCoord, quaternionMulCoord, quaternionAddCoord, quaternionNegCoord,
    quaternionSubCoord]
  ring

theorem unitOctonion_mul_closed (a b : OctonionCoord)
    (ha : octonionCoordNormSq a = 1) (hb : octonionCoordNormSq b = 1) :
    octonionCoordNormSq (octonionMulCoord a b) = 1 := by
  rw [octonionNormMul, ha, hb]
  ring

theorem octonion_noncommutative_example :
    octonionMulCoord (octonionBasisCoord ⟨1, by norm_num⟩) (octonionBasisCoord ⟨2, by norm_num⟩) ≠
      octonionMulCoord (octonionBasisCoord ⟨2, by norm_num⟩) (octonionBasisCoord ⟨1, by norm_num⟩) := by
  norm_num [octonionBasisCoord, octonionMulCoord, quaternionMulCoord, quaternionConjCoord,
    quaternionAddCoord, quaternionNegCoord, quaternionSubCoord]

theorem octonion_nonassociative_example :
    octonionMulCoord
        (octonionMulCoord (octonionBasisCoord ⟨1, by norm_num⟩) (octonionBasisCoord ⟨2, by norm_num⟩))
        (octonionBasisCoord ⟨4, by norm_num⟩) ≠
      octonionMulCoord
        (octonionBasisCoord ⟨1, by norm_num⟩)
        (octonionMulCoord (octonionBasisCoord ⟨2, by norm_num⟩) (octonionBasisCoord ⟨4, by norm_num⟩)) := by
  norm_num [octonionBasisCoord, octonionMulCoord, quaternionMulCoord, quaternionConjCoord,
    quaternionAddCoord, quaternionNegCoord, quaternionSubCoord]

def octonionTrackName : String :=
  "S7O"

end Circle.S7
