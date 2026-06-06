import Circle.S3.Scaffold

/-!
S3.3 sidecar.

This file re-exports the bounded Lean Hopf-coordinate declarations used by
`papers/S3/PAPER_S3_03_HOPF_COILS.md`.
-/

namespace Circle.PaperS303

#check Circle.S3.HopfPair
#check Circle.S3.HopfBasePoint
#check Circle.S3.hopfPairNormSq
#check Circle.S3.hopfBaseNormSq
#check Circle.S3.hopfMap
#check Circle.S3.hopfBaseNormSq_hopfMap
#check Circle.S3.hopfMap_lands_sphere
#check Circle.S3.phaseRotatePair
#check Circle.S3.HopfPhase
#check Circle.S3.hopfPhaseIdentity
#check Circle.S3.hopfPhaseMul
#check Circle.S3.hopfPhaseMul_identity
#check Circle.S3.hopfPhaseMul_assoc
#check Circle.S3.hopfPhaseAct
#check Circle.S3.phaseRotatePair_identity
#check Circle.S3.phaseRotatePair_comp
#check Circle.S3.hopfPhaseAct_identity
#check Circle.S3.hopfPhaseAct_comp
#check Circle.S3.hopfPhaseAction_laws
#check Circle.S3.phaseRotatePair_norm_sq
#check Circle.S3.hopfMap_phase_invariant
#check Circle.S3.hopfFiber_circle_like

end Circle.PaperS303
