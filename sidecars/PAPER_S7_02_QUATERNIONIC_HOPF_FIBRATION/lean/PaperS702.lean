import Circle.S7.Scaffold

/-!
S7.2 sidecar.

This file re-exports the bounded Lean quaternionic Hopf-coordinate declarations used by
`papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md`.
-/

namespace Circle.PaperS702

#check Circle.S7.QuaternionCoord
#check Circle.S7.QuaternionPair
#check Circle.S7.HopfBase5
#check Circle.S7.quaternionCoordNormSq
#check Circle.S7.quaternionConjCoord
#check Circle.S7.quaternionMulCoord
#check Circle.S7.quaternionCoord_ext
#check Circle.S7.quaternionMulCoord_assoc
#check Circle.S7.quaternionPairNormSq
#check Circle.S7.quaternionPairRightPhase
#check Circle.S7.quaternionPairRightPhase_comp
#check Circle.S7.hopfBase5NormSq
#check Circle.S7.hopfBase5Scale
#check Circle.S7.quaternionicHopfMap
#check Circle.S7.quaternionCoordNormSq_mul
#check Circle.S7.quaternionCoordNormSq_conj
#check Circle.S7.quaternionicHopfBaseNormSq_hopfMap
#check Circle.S7.quaternionicHopf_lands_sphere
#check Circle.S7.quaternionicHopfMap_rightPhase_scaled
#check Circle.S7.quaternionicPhaseInvariance
#check Circle.S7.quaternionicRightPhaseAction_laws

end Circle.PaperS702
