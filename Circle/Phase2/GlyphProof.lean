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

def proofGlyph (glyphId theoremId leanName : String) : ProofGlyph :=
  { glyphId := glyphId, theoremId := theoremId, leanName := leanName }

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

end Circle.Phase2
