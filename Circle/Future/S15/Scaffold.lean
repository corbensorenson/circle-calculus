import Circle.Common.Scaffold
import Circle.S7.Scaffold

namespace Circle.Future.S15

def dimension : Nat := 15

def eightSuspensions (cells : List Nat) : List Nat :=
  Circle.Common.suspensionCounts
    (Circle.Common.suspensionCounts
      (Circle.Common.suspensionCounts
        (Circle.Common.suspensionCounts
          (Circle.Common.suspensionCounts
            (Circle.Common.suspensionCounts
              (Circle.Common.suspensionCounts
                (Circle.Common.suspensionCounts cells)))))))

def topologicalModel (n : Nat) : List Nat :=
  eightSuspensions (Circle.S7.iteratedSuspensionModel n)

theorem topologicalModel_eq_eightSuspensions_s7 (n : Nat) :
    topologicalModel n = eightSuspensions (Circle.S7.iteratedSuspensionModel n) := by
  rfl

theorem topologicalModel_eulerCharacteristic (n : Nat) :
    Circle.Common.eulerCharacteristic (topologicalModel n) = 0 := by
  unfold topologicalModel eightSuspensions
  repeat rw [Circle.Common.suspensionEuler]
  rw [Circle.S7.eulerCharacteristic]
  norm_num

structure OctonionPair where
  o0 : Circle.S7.OctonionCoord
  o1 : Circle.S7.OctonionCoord

structure HopfBase9 where
  oct : Circle.S7.OctonionCoord
  scalar : ℝ

def octonionScaleCoord (s : ℝ) (o : Circle.S7.OctonionCoord) : Circle.S7.OctonionCoord where
  left :=
    { r := s * o.left.r
      i := s * o.left.i
      j := s * o.left.j
      k := s * o.left.k }
  right :=
    { r := s * o.right.r
      i := s * o.right.i
      j := s * o.right.j
      k := s * o.right.k }

def octonionPairNormSq (p : OctonionPair) : ℝ :=
  Circle.S7.octonionCoordNormSq p.o0 + Circle.S7.octonionCoordNormSq p.o1

def hopfBase9NormSq (p : HopfBase9) : ℝ :=
  Circle.S7.octonionCoordNormSq p.oct + p.scalar * p.scalar

def octonionicHopfMap (p : OctonionPair) : HopfBase9 where
  oct := octonionScaleCoord 2 (Circle.S7.octonionMulCoord p.o0 (Circle.S7.octonionConjCoord p.o1))
  scalar := Circle.S7.octonionCoordNormSq p.o0 - Circle.S7.octonionCoordNormSq p.o1

def octonionPairRightPhase (p : OctonionPair) (u : Circle.S7.OctonionCoord) : OctonionPair where
  o0 := Circle.S7.octonionMulCoord p.o0 u
  o1 := Circle.S7.octonionMulCoord p.o1 u

theorem octonionCoordNormSq_scale (s : ℝ) (o : Circle.S7.OctonionCoord) :
    Circle.S7.octonionCoordNormSq (octonionScaleCoord s o) =
      s * s * Circle.S7.octonionCoordNormSq o := by
  rcases o with ⟨⟨a, b, c, d⟩, ⟨e, f, g, h⟩⟩
  simp [octonionScaleCoord, Circle.S7.octonionCoordNormSq,
    Circle.S7.quaternionCoordNormSq]
  ring

theorem octonionCoordNormSq_conj (o : Circle.S7.OctonionCoord) :
    Circle.S7.octonionCoordNormSq (Circle.S7.octonionConjCoord o) =
      Circle.S7.octonionCoordNormSq o := by
  rcases o with ⟨⟨a, b, c, d⟩, ⟨e, f, g, h⟩⟩
  simp [Circle.S7.octonionConjCoord, Circle.S7.octonionCoordNormSq,
    Circle.S7.quaternionCoordNormSq, Circle.S7.quaternionConjCoord,
    Circle.S7.quaternionNegCoord]

theorem hopfBase9NormSq_octonionicHopfMap (p : OctonionPair) :
    hopfBase9NormSq (octonionicHopfMap p) =
      octonionPairNormSq p * octonionPairNormSq p := by
  simp [hopfBase9NormSq, octonionicHopfMap, octonionPairNormSq]
  rw [octonionCoordNormSq_scale, Circle.S7.octonionNormMul, octonionCoordNormSq_conj]
  ring

theorem octonionicHopf_lands_sphere (p : OctonionPair)
    (h : octonionPairNormSq p = 1) :
    hopfBase9NormSq (octonionicHopfMap p) = 1 := by
  rw [hopfBase9NormSq_octonionicHopfMap, h]
  ring

theorem octonionPairRightPhase_normSq (p : OctonionPair)
    (u : Circle.S7.OctonionCoord) :
    octonionPairNormSq (octonionPairRightPhase p u) =
      octonionPairNormSq p * Circle.S7.octonionCoordNormSq u := by
  simp [octonionPairRightPhase, octonionPairNormSq, Circle.S7.octonionNormMul]
  ring

theorem octonionicHopfMap_rightPhase_scalar_invariant (p : OctonionPair)
    (u : Circle.S7.OctonionCoord)
    (hu : Circle.S7.octonionCoordNormSq u = 1) :
    (octonionicHopfMap (octonionPairRightPhase p u)).scalar =
      (octonionicHopfMap p).scalar := by
  simp [octonionicHopfMap, octonionPairRightPhase, Circle.S7.octonionNormMul, hu]

theorem octonionicHopfMap_rightPhase_lands_sphere (p : OctonionPair)
    (u : Circle.S7.OctonionCoord)
    (hp : octonionPairNormSq p = 1)
    (hu : Circle.S7.octonionCoordNormSq u = 1) :
    hopfBase9NormSq (octonionicHopfMap (octonionPairRightPhase p u)) = 1 := by
  apply octonionicHopf_lands_sphere
  rw [octonionPairRightPhase_normSq, hp, hu]
  ring

theorem octonionicHopfMap_rightPhase_not_invariant_example :
    octonionicHopfMap
        (octonionPairRightPhase
          { o0 := Circle.S7.octonionBasisCoord ⟨1, by norm_num⟩
            o1 := Circle.S7.octonionBasisCoord ⟨2, by norm_num⟩ }
          (Circle.S7.octonionBasisCoord ⟨4, by norm_num⟩)) ≠
      octonionicHopfMap
        { o0 := Circle.S7.octonionBasisCoord ⟨1, by norm_num⟩
          o1 := Circle.S7.octonionBasisCoord ⟨2, by norm_num⟩ } := by
  norm_num [octonionPairRightPhase, octonionicHopfMap, octonionScaleCoord,
    Circle.S7.octonionBasisCoord, Circle.S7.octonionMulCoord,
    Circle.S7.octonionConjCoord, Circle.S7.quaternionConjCoord,
    Circle.S7.quaternionMulCoord, Circle.S7.quaternionAddCoord,
    Circle.S7.quaternionNegCoord, Circle.S7.quaternionSubCoord]

def octonionicHopfRoadmap : String :=
  "S7 -> S15 -> S8"

def roadmapName : String :=
  "S15-T0001"

end Circle.Future.S15
