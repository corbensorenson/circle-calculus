import Circle.Applications.CircleAI

/-!
AI 3 sidecar.

This file re-exports the adapter-block seed used by
`papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md`.
-/

namespace Circle.PaperAI03

#check Circle.Applications.adapterBlock
#check Circle.Applications.adapterBlock_lt_blockSize
#check Circle.Applications.adapterBlock_add_blockSize
#check Circle.Applications.adapterBlock_add_mul_blockSize
#check Circle.Applications.adapterBlock_idempotent
#check Circle.Applications.adapterBlock_zero
#check Circle.Applications.blockCyclicCell
#check Circle.Applications.blockCyclicCell_fst_lt_blockSize
#check Circle.Applications.blockCyclicCell_snd_lt_blockSize
#check Circle.Applications.blockCyclicCell_add_row_blockSize
#check Circle.Applications.blockCyclicCell_add_column_blockSize
#check Circle.Applications.blockCyclicCell_add_mul_blockSize
#check Circle.Applications.positionResidue
#check Circle.Applications.positionWinding
#check Circle.Applications.windingPosition
#check Circle.Applications.positionResidue_lt_period
#check Circle.Applications.positionResidue_add_period
#check Circle.Applications.positionResidue_add_mul_period
#check Circle.Applications.positionWinding_mul_add_residue
#check Circle.Applications.windingPosition_fst_mul_add_snd

end Circle.PaperAI03
