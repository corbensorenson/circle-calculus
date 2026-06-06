import Circle.Basic

/-!
Paper 1 sidecar.

This file re-exports the v0 finite-circle core declarations used by the paper.
The canonical theorem ids live in `manifests/theorem_manifest.yaml`.
-/

namespace Circle.Paper01

#check Circle.rot_zero
#check Circle.rot_comp
#check Circle.rot_inverse_left
#check Circle.closesAt_iff_stride_multiple_zero
#check Circle.period_eq_n_div_gcd
#check Circle.orbit_decomposition_count
#check Circle.sameOrbit_iff_difference_mem_orbitSubgroup
#check Circle.sameOrbit_nat_modEq_gcd_of_sameOrbit
#check Circle.sameOrbit_of_nat_modEq_gcd
#check Circle.sameOrbit_nat_iff_modEq_gcd
#check Circle.fullCoil_iff_coprime
#check Circle.prime_full_coil

end Circle.Paper01
