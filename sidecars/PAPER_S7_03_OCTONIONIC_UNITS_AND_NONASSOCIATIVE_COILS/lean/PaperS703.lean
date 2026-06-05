import Circle.S7.Scaffold

/-!
S7.3 sidecar.

This file re-exports the bounded Lean Cayley-Dickson octonion declarations used by
`papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md`.
-/

namespace Circle.PaperS703

#check Circle.S7.OctonionCoord
#check Circle.S7.octonionCoordNormSq
#check Circle.S7.octonionConjCoord
#check Circle.S7.octonionRealCoord
#check Circle.S7.octonionMulCoord
#check Circle.S7.octonionBasisCoord
#check Circle.S7.octonionBasis
#check Circle.S7.octonionConjugateNorm
#check Circle.S7.octonion_noncommutative_example
#check Circle.S7.octonion_nonassociative_example

end Circle.PaperS703
