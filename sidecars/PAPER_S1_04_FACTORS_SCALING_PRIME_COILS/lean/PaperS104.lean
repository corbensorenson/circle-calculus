import Circle.Basic

/-!
S1.4 sidecar.

This file re-exports the scaling declaration and first proved scaling theorem.
The canonical theorem ids live in `manifests/theorem_manifest.yaml`.
-/

namespace Circle.PaperS104

#check Circle.scale
#check Circle.scale_zero_factor
#check Circle.scale_one
#check Circle.scale_comp
#check Circle.scale_rot
#check Circle.scale_coilStep
#check Circle.scale_nat_to_coilStep
#check Circle.scale_invertible_iff_coprime
#check Circle.prime_scale_bijective
#check Circle.scale_cofactor_zero
#check Circle.scale_cofactor_multiple_zero
#check Circle.scale_add_cofactor_multiple
#check Circle.scale_nat_eq_zero_iff_dvd_mul
#check Circle.scale_nat_eq_zero_iff_period_dvd
#check Circle.scale_period_multiple_zero
#check Circle.scale_add_period_multiple
#check Circle.scale_nat_period_normalForm
#check Circle.scale_nat_eq_iff_mul_modEq
#check Circle.scale_nat_eq_iff_period_modEq
#check Circle.scale_nat_period_representatives_injective
#check Circle.scalePeriodRepresentativeImage
#check Circle.scalePeriodRepresentativeImage_card
#check Circle.scale_nat_mem_scalePeriodRepresentativeImage
#check Circle.scaleCircleImage
#check Circle.scaleCircleImage_eq_scalePeriodRepresentativeImage
#check Circle.scaleCircleImage_card
#check Circle.scaleKernelRepresentativeSet
#check Circle.scalePeriodKernelRepresentatives
#check Circle.scalePeriodKernelRepresentatives_card
#check Circle.scaleKernelRepresentativeSet_eq_periodMultiples
#check Circle.scaleKernelRepresentativeSet_card
#check Circle.scale_nat_eq_iff_nat_modEq_of_coprime
#check Circle.scale_factor_modEq

end Circle.PaperS104
