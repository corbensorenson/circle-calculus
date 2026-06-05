import Circle.Common.Scaffold
import Circle.S6.Scaffold

namespace Circle.S7

def dimension : Nat := 7

def iteratedSuspensionModel (n : Nat) : List Nat :=
  Circle.Common.suspensionCounts (Circle.S6.counts n)

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

structure QuaternionPair where
  q0 : QuaternionCoord
  q1 : QuaternionCoord

structure HopfBase5 where
  x0 : ℝ
  x1 : ℝ
  x2 : ℝ
  x3 : ℝ
  x4 : ℝ

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

def hopfBase5NormSq (p : HopfBase5) : ℝ :=
  p.x0 * p.x0 + p.x1 * p.x1 + p.x2 * p.x2 + p.x3 * p.x3 + p.x4 * p.x4

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

def octonionTrackName : String :=
  "S7O"

end Circle.S7
