import Circle.S3.Scaffold

/-!
S3.2 sidecar.

This file re-exports the quaternion declarations used by
`papers/S3/PAPER_S3_02_QUATERNION_COILS.md`.
-/

namespace Circle.PaperS302

#check Circle.S3.RealQuaternion
#check Circle.S3.quaternionNorm
#check Circle.S3.UnitQuaternion
#check Circle.S3.unitQuaternion_mul_closed
#check Circle.S3.unitQuaternionMul
#check Circle.S3.unitQuaternion_inverse
#check Circle.S3.quaternionI
#check Circle.S3.quaternionJ
#check Circle.S3.quaternion_noncommutative_example
#check Circle.S3.quaternion_mul_assoc

end Circle.PaperS302
