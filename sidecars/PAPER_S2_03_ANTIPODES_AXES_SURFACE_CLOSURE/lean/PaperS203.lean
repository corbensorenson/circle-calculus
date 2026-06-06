import Circle.S2.Scaffold

/-!
S2.3 sidecar.

This file re-exports the finite antipode declarations used by
`papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md`.
-/

namespace Circle.PaperS203

#check Circle.S2.SuspendedCirclePoint
#check Circle.S2.suspendedCircleAntipode
#check Circle.S2.suspendedCircleLongitudeRotation
#check Circle.S2.isSuspendedPole
#check Circle.S2.isSuspendedEquator
#check Circle.S2.suspendedCircleAntipodalPair
#check Circle.S2.suspendedCircleAntipode_swapsPoles
#check Circle.S2.suspendedCircleAntipode_involutive
#check Circle.S2.suspendedCircleAntipode_bijective
#check Circle.S2.suspendedCircleAntipode_longitudeRotation_opposite
#check Circle.S2.suspendedCircleAntipode_preservesPoleSet
#check Circle.S2.suspendedCircleAntipode_preservesEquatorSet
#check Circle.S2.suspendedCircleAntipodalPair_self_antipode
#check Circle.S2.suspendedCircleAntipodalPair_symmetric
#check Circle.S2.sphereGridLatitudeCoordinate
#check Circle.S2.sphereGridLongitudeCoordinate
#check Circle.S2.longitudeRotation_preservesLatitudeCoordinate
#check Circle.S2.longitudeRotation_advancesLongitudeCoordinate

end Circle.PaperS203
