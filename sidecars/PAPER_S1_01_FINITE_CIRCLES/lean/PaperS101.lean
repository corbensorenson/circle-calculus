import Circle.Basic

/-!
S1.1 sidecar.

This file re-exports the finite circle declarations used by
`papers/S1/PAPER_S1_01_FINITE_CIRCLES.md`.
-/

namespace Circle.PaperS101

#check Circle.C
#check Circle.rot_zero
#check Circle.rot_comp
#check Circle.rot_inverse_left
#check Circle.closesAt_iff_stride_multiple_zero
#check Circle.period_eq_n_div_gcd
#check Circle.orbit_decomposition_count
#check Circle.prime_full_coil

end Circle.PaperS101
