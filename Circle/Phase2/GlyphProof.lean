/-!
Phase II proof-carrying glyph seed.

This module formalizes only the certificate record that connects a glyph to a
theorem id and Lean declaration name. It does not formalize rendering,
normalization, or proof search.
-/

namespace Circle.Phase2

structure ProofGlyph where
  glyphId : String
  theoremId : String
  leanName : String

structure TheoremMetadata where
  theoremId : String
  leanName : String

def proofGlyph (glyphId theoremId leanName : String) : ProofGlyph :=
  { glyphId := glyphId, theoremId := theoremId, leanName := leanName }

def theoremMetadata (theoremId leanName : String) : TheoremMetadata :=
  { theoremId := theoremId, leanName := leanName }

def proofGlyphGlyphId (glyph : ProofGlyph) : String :=
  glyph.glyphId

def proofGlyphTheoremId (glyph : ProofGlyph) : String :=
  glyph.theoremId

def proofGlyphLeanName (glyph : ProofGlyph) : String :=
  glyph.leanName

theorem proofGlyphGlyphId_mk (glyphId theoremId leanName : String) :
    proofGlyphGlyphId (proofGlyph glyphId theoremId leanName) = glyphId := by
  rfl

theorem proofGlyphTheoremId_mk (glyphId theoremId leanName : String) :
    proofGlyphTheoremId (proofGlyph glyphId theoremId leanName) = theoremId := by
  rfl

theorem proofGlyphLeanName_mk (glyphId theoremId leanName : String) :
    proofGlyphLeanName (proofGlyph glyphId theoremId leanName) = leanName := by
  rfl

def proofGlyphMatchesMetadata (glyph : ProofGlyph) (metadata : TheoremMetadata) : Prop :=
  proofGlyphTheoremId glyph = metadata.theoremId ∧
    proofGlyphLeanName glyph = metadata.leanName

def proofGlyphValidAgainst (glyph : ProofGlyph) (manifest : List TheoremMetadata) : Prop :=
  ∃ metadata, metadata ∈ manifest ∧ proofGlyphMatchesMetadata glyph metadata

theorem proofGlyphValidAgainst_resolves_metadata
    (glyph : ProofGlyph) (manifest : List TheoremMetadata)
    (h : proofGlyphValidAgainst glyph manifest) :
    ∃ metadata, metadata ∈ manifest ∧
      proofGlyphTheoremId glyph = metadata.theoremId ∧
      proofGlyphLeanName glyph = metadata.leanName := by
  exact h

theorem proofGlyphValidAgainst_of_matching_metadata
    (glyph : ProofGlyph) (manifest : List TheoremMetadata) (metadata : TheoremMetadata)
    (hin : metadata ∈ manifest)
    (htheorem : proofGlyphTheoremId glyph = metadata.theoremId)
    (hlean : proofGlyphLeanName glyph = metadata.leanName) :
    proofGlyphValidAgainst glyph manifest := by
  exact ⟨metadata, hin, htheorem, hlean⟩

end Circle.Phase2
