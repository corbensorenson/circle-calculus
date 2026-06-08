import Circle.Basic
import Circle.Phase2.GlyphProof

/-!
Finite seed-rule provenance seeds for Circle Calculus.

This module formalizes exact regeneration checks for small bounded records. It
does not prove minimality, compression optimality, or universal generative
claims.
-/

namespace Circle.Generative

structure FiniteCircleGenerator where
  n : Nat

def finiteCircleGenerator (n : Nat) : FiniteCircleGenerator :=
  { n := n }

def FiniteCircleGenerator.generatedNodes (generator : FiniteCircleGenerator) : List Nat :=
  List.range generator.n

theorem finiteCircleGenerator_regenerates_nodes (n : Nat) :
    (finiteCircleGenerator n).generatedNodes = List.range n := by
  rfl

theorem finiteCircleGenerator_generatedNodes_length (n : Nat) :
    (finiteCircleGenerator n).generatedNodes.length = n := by
  simp [FiniteCircleGenerator.generatedNodes, finiteCircleGenerator]

structure CoilOrbitGenerator where
  n : Nat
  stride : Nat
  start : Nat

def coilOrbitGenerator (n stride start : Nat) : CoilOrbitGenerator :=
  { n := n, stride := stride, start := start }

noncomputable def CoilOrbitGenerator.period (generator : CoilOrbitGenerator) : Nat :=
  Circle.period generator.n generator.stride

noncomputable def CoilOrbitGenerator.generatedOrbit
    (generator : CoilOrbitGenerator) : List (C generator.n) :=
  List.ofFn fun step : Fin generator.period =>
    Circle.coilStep generator.n generator.stride generator.start step

theorem coilOrbitGenerator_regenerates_orbit (n stride start : Nat) :
    (coilOrbitGenerator n stride start).generatedOrbit =
      List.ofFn (fun step : Fin (Circle.period n stride) =>
        Circle.coilStep n stride start step) := by
  rfl

theorem coilOrbitGenerator_generatedOrbit_length (n stride start : Nat) :
    (coilOrbitGenerator n stride start).generatedOrbit.length =
      Circle.period n stride := by
  simp [CoilOrbitGenerator.generatedOrbit, CoilOrbitGenerator.period,
    coilOrbitGenerator]

structure OrbitDecompositionGenerator where
  n : Nat
  stride : Nat

def orbitDecompositionGenerator (n stride : Nat) : OrbitDecompositionGenerator :=
  { n := n, stride := stride }

def OrbitDecompositionGenerator.orbitCount (generator : OrbitDecompositionGenerator) : Nat :=
  Nat.gcd generator.n generator.stride

noncomputable def OrbitDecompositionGenerator.orbitPeriod
    (generator : OrbitDecompositionGenerator) : Nat :=
  Circle.period generator.n generator.stride

noncomputable def OrbitDecompositionGenerator.generatedOrbitFor
    (generator : OrbitDecompositionGenerator)
    (start : Fin generator.orbitCount) : List (C generator.n) :=
  List.ofFn fun step : Fin generator.orbitPeriod =>
    Circle.coilStep generator.n generator.stride start step

noncomputable def OrbitDecompositionGenerator.generatedOrbits
    (generator : OrbitDecompositionGenerator) : List (List (C generator.n)) :=
  List.ofFn fun start : Fin generator.orbitCount =>
    generator.generatedOrbitFor start

theorem orbitDecompositionGenerator_regenerates_orbits (n stride : Nat) :
    (orbitDecompositionGenerator n stride).generatedOrbits =
      List.ofFn (fun start : Fin (Nat.gcd n stride) =>
        List.ofFn fun step : Fin (Circle.period n stride) =>
          Circle.coilStep n stride start step) := by
  rfl

theorem orbitDecompositionGenerator_generatedOrbits_length (n stride : Nat) :
    (orbitDecompositionGenerator n stride).generatedOrbits.length =
      Nat.gcd n stride := by
  simp [OrbitDecompositionGenerator.generatedOrbits,
    OrbitDecompositionGenerator.orbitCount, orbitDecompositionGenerator]

theorem orbitDecompositionGenerator_generatedOrbitFor_length
    (n stride : Nat) (start : Fin (Nat.gcd n stride)) :
    ((orbitDecompositionGenerator n stride).generatedOrbitFor start).length =
      Circle.period n stride := by
  simp [OrbitDecompositionGenerator.generatedOrbitFor,
    OrbitDecompositionGenerator.orbitPeriod, orbitDecompositionGenerator]

theorem orbitDecompositionGenerator_orbitCount_mul_period
    {n stride : Nat} (hn : n ≠ 0) :
    (orbitDecompositionGenerator n stride).orbitCount *
        (orbitDecompositionGenerator n stride).orbitPeriod = n := by
  simp [OrbitDecompositionGenerator.orbitCount,
    OrbitDecompositionGenerator.orbitPeriod, orbitDecompositionGenerator,
    Circle.period_eq_n_div_gcd hn]
  rw [Nat.mul_comm]
  exact Nat.div_mul_cancel (Nat.gcd_dvd_left n stride)

theorem orbitDecompositionGenerator_orbitCount_eq_orbitClassCount
    {n stride : Nat} (hn : n ≠ 0) :
    (orbitDecompositionGenerator n stride).orbitCount =
      Circle.orbitClassCount n stride := by
  rw [Circle.orbit_decomposition_count (n := n) (k := stride) hn]
  rfl

theorem orbitDecompositionGenerator_modRepresentative_lt_orbitCount
    {n stride x : Nat}
    (hpositive : 0 < (orbitDecompositionGenerator n stride).orbitCount) :
    x % (orbitDecompositionGenerator n stride).orbitCount <
      (orbitDecompositionGenerator n stride).orbitCount := by
  exact Nat.mod_lt x hpositive

theorem orbitDecompositionGenerator_modRepresentative_covers
    (n stride x : Nat) :
    Circle.sameOrbit n stride
      (((x % (orbitDecompositionGenerator n stride).orbitCount) : Nat) : C n)
      ((x : Nat) : C n) := by
  simpa [OrbitDecompositionGenerator.orbitCount, orbitDecompositionGenerator] using
    (Circle.sameOrbit_nat_iff_modEq_gcd
      n stride (x % Nat.gcd n stride) x).mpr
        (Nat.mod_modEq x (Nat.gcd n stride))

theorem orbitDecompositionGenerator_representatives_sameOrbit_iff_eq
    (n stride : Nat)
    (left right : Fin (orbitDecompositionGenerator n stride).orbitCount) :
    Circle.sameOrbit n stride ((left : Nat) : C n) ((right : Nat) : C n) ↔
      left = right := by
  constructor
  · intro h
    have hmod :
        (left : Nat) ≡ (right : Nat) [MOD Nat.gcd n stride] :=
      (Circle.sameOrbit_nat_iff_modEq_gcd n stride (left : Nat) (right : Nat)).mp h
    have hleft : (left : Nat) < Nat.gcd n stride := by
      simp [OrbitDecompositionGenerator.orbitCount, orbitDecompositionGenerator]
    have hright : (right : Nat) < Nat.gcd n stride := by
      simp [OrbitDecompositionGenerator.orbitCount, orbitDecompositionGenerator]
    exact Fin.ext (Nat.ModEq.eq_of_lt_of_lt hmod hleft hright)
  · intro h
    subst h
    exact (Circle.sameOrbit_nat_iff_modEq_gcd n stride (left : Nat) (left : Nat)).mpr
      (Nat.ModEq.refl (left : Nat))

theorem orbitDecompositionGenerator_distinct_representatives_disjoint
    (n stride : Nat)
    (left right : Fin (orbitDecompositionGenerator n stride).orbitCount)
    (hdistinct : left ≠ right) :
    ¬ Circle.sameOrbit n stride ((left : Nat) : C n) ((right : Nat) : C n) := by
  intro hsame
  exact hdistinct
    ((orbitDecompositionGenerator_representatives_sameOrbit_iff_eq n stride left right).mp hsame)

structure ProofGlyphGenerator where
  glyphId : String
  theoremId : String
  leanName : String

def proofGlyphGenerator (glyphId theoremId leanName : String) : ProofGlyphGenerator :=
  { glyphId := glyphId, theoremId := theoremId, leanName := leanName }

def ProofGlyphGenerator.generatedCertificate
    (generator : ProofGlyphGenerator) : Circle.Phase2.ProofGlyph :=
  Circle.Phase2.proofGlyph generator.glyphId generator.theoremId generator.leanName

theorem proofGlyphGenerator_regenerates_certificate
    (glyphId theoremId leanName : String) :
    let generator := proofGlyphGenerator glyphId theoremId leanName
    Circle.Phase2.proofGlyphGlyphId generator.generatedCertificate = glyphId ∧
      Circle.Phase2.proofGlyphTheoremId generator.generatedCertificate = theoremId ∧
      Circle.Phase2.proofGlyphLeanName generator.generatedCertificate = leanName := by
  simp [proofGlyphGenerator, ProofGlyphGenerator.generatedCertificate,
    Circle.Phase2.proofGlyphGlyphId, Circle.Phase2.proofGlyphTheoremId,
    Circle.Phase2.proofGlyphLeanName, Circle.Phase2.proofGlyph]

structure GeneratorComparison (α : Type) where
  regenerated : α
  generated : α
  exactRegeneration : Prop

def generatorComparison (regenerated generated : α) : GeneratorComparison α :=
  { regenerated := regenerated,
    generated := generated,
    exactRegeneration := regenerated = generated }

theorem generatorComparison_requires_exact_regeneration
    (regenerated generated : α) :
    (generatorComparison regenerated generated).exactRegeneration ↔ regenerated = generated := by
  rfl

theorem generatorComparison_self_exact (value : α) :
    (generatorComparison value value).exactRegeneration := by
  rfl

theorem generatorComparison_exact_regeneration_symm
    (regenerated generated : α) :
    (generatorComparison regenerated generated).exactRegeneration →
      (generatorComparison generated regenerated).exactRegeneration := by
  intro h
  exact h.symm

theorem generatorComparison_exact_regeneration_trans
    (first second third : α) :
    (generatorComparison first second).exactRegeneration →
      (generatorComparison second third).exactRegeneration →
      (generatorComparison first third).exactRegeneration := by
  intro hfirst hsecond
  exact hfirst.trans hsecond

theorem generatorComparison_exact_regeneration_iff_fields_eq
    (regenerated generated : α) :
    (generatorComparison regenerated generated).exactRegeneration ↔
      (generatorComparison regenerated generated).regenerated =
        (generatorComparison regenerated generated).generated := by
  rfl

theorem generatorComparison_exact_regeneration_fields_eq
    (regenerated generated : α) :
    (generatorComparison regenerated generated).exactRegeneration →
      (generatorComparison regenerated generated).regenerated =
        (generatorComparison regenerated generated).generated := by
  intro h
  exact h

theorem generatorComparison_not_exact_of_ne
    (regenerated generated : α) :
    regenerated ≠ generated →
      ¬ (generatorComparison regenerated generated).exactRegeneration := by
  intro hne hexact
  exact hne hexact

structure BoundedGeneratorSearch (α : Type) where
  candidates : List (GeneratorComparison α)
  exactCandidates : List (GeneratorComparison α)
  exactSubset :
    ∀ candidate, candidate ∈ exactCandidates → candidate ∈ candidates
  exactSound :
    ∀ candidate, candidate ∈ exactCandidates → candidate.exactRegeneration

def emptyBoundedGeneratorSearch (α : Type) : BoundedGeneratorSearch α :=
  { candidates := [],
    exactCandidates := [],
    exactSubset := (by
      intro candidate hmember
      cases hmember),
    exactSound := (by
      intro candidate hmember
      cases hmember) }

def BoundedGeneratorSearch.candidateCount
    (search : BoundedGeneratorSearch α) : Nat :=
  search.candidates.length

def BoundedGeneratorSearch.exactCandidateCount
    (search : BoundedGeneratorSearch α) : Nat :=
  search.exactCandidates.length

def BoundedGeneratorSearch.bestExact?
    (search : BoundedGeneratorSearch α) : Option (GeneratorComparison α) :=
  search.exactCandidates.head?

theorem emptyBoundedGeneratorSearch_candidateCount (α : Type) :
    (emptyBoundedGeneratorSearch α).candidateCount = 0 := by
  rfl

theorem emptyBoundedGeneratorSearch_exactCandidateCount (α : Type) :
    (emptyBoundedGeneratorSearch α).exactCandidateCount = 0 := by
  rfl

theorem emptyBoundedGeneratorSearch_bestExact_none (α : Type) :
    (emptyBoundedGeneratorSearch α).bestExact? = none := by
  rfl

theorem boundedGeneratorSearch_bestExact_mem_exactCandidates
    (search : BoundedGeneratorSearch α) {candidate : GeneratorComparison α}
    (hbest : search.bestExact? = some candidate) :
    candidate ∈ search.exactCandidates := by
  apply List.mem_of_mem_head?
  simpa [BoundedGeneratorSearch.bestExact?, hbest]

theorem boundedGeneratorSearch_bestExact_mem_candidates
    (search : BoundedGeneratorSearch α) {candidate : GeneratorComparison α}
    (hbest : search.bestExact? = some candidate) :
    candidate ∈ search.candidates :=
  search.exactSubset candidate
    (boundedGeneratorSearch_bestExact_mem_exactCandidates search hbest)

theorem boundedGeneratorSearch_bestExact_exact
    (search : BoundedGeneratorSearch α) {candidate : GeneratorComparison α}
    (hbest : search.bestExact? = some candidate) :
    candidate.exactRegeneration :=
  search.exactSound candidate
    (boundedGeneratorSearch_bestExact_mem_exactCandidates search hbest)

theorem boundedGeneratorSearch_bestExact_none_iff_exactCandidates_empty
    (search : BoundedGeneratorSearch α) :
    search.bestExact? = none ↔ search.exactCandidates = [] := by
  cases search with
  | mk candidates exactCandidates exactSubset exactSound =>
      cases exactCandidates <;> simp [BoundedGeneratorSearch.bestExact?]

theorem boundedGeneratorSearch_bestExact_none_iff_exactCandidateCount_zero
    (search : BoundedGeneratorSearch α) :
    search.bestExact? = none ↔ search.exactCandidateCount = 0 := by
  cases search with
  | mk candidates exactCandidates exactSubset exactSound =>
      cases exactCandidates <;>
        simp [BoundedGeneratorSearch.bestExact?,
          BoundedGeneratorSearch.exactCandidateCount]

theorem boundedGeneratorSearch_bestExact_some_exactCandidateCount_pos
    (search : BoundedGeneratorSearch α) {candidate : GeneratorComparison α}
    (hbest : search.bestExact? = some candidate) :
    0 < search.exactCandidateCount := by
  cases search with
  | mk candidates exactCandidates exactSubset exactSound =>
      cases exactCandidates with
      | nil =>
          simp [BoundedGeneratorSearch.bestExact?] at hbest
      | cons head tail =>
          simp [BoundedGeneratorSearch.exactCandidateCount]

end Circle.Generative
