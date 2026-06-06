import Circle.S3.Scaffold

/-!
S3.4 sidecar.

This file re-exports the quaternion sign-cancellation declaration used by
`papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md`.
-/

namespace Circle.PaperS304

#check Circle.S3.quaternionConjugationAction
#check Circle.S3.quaternionConjugation_one
#check Circle.S3.quaternionConjugation_zero_vector
#check Circle.S3.quaternionConjugation_neg
#check Circle.S3.unitQuaternionNeg
#check Circle.S3.unitQuaternion_neg_involutive
#check Circle.S3.spinSignRelated
#check Circle.S3.spinSignRelated_refl
#check Circle.S3.spinSignRelated_symm
#check Circle.S3.spinSignRelated_trans
#check Circle.S3.spinSignRelated_equivalence

end Circle.PaperS304
