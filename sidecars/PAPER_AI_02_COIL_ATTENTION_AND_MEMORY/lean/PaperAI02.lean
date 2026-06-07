import Circle.Applications.CircleAI

/-!
AI 2 sidecar.

This file re-exports the cyclic memory-slot seed used by
`papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`.
-/

namespace Circle.PaperAI02

#check Circle.Applications.memorySlot
#check Circle.Applications.memorySlot_lt_bankSize
#check Circle.Applications.memorySlot_add_bankSize
#check Circle.Applications.memorySlot_add_mul_bankSize
#check Circle.Applications.memorySlot_idempotent
#check Circle.Applications.memorySlot_zero
#check Circle.Applications.loopRequiredSteps_pos
#check Circle.Applications.loopRequiredSteps_le_loopPeriod
#check Circle.Applications.loopRequiredSteps_add_loopPeriod
#check Circle.Applications.tokenRecurrenceBudget_add_loopPeriod
#check Circle.Applications.trainingFreeLoopBudget_le_maxLoops

end Circle.PaperAI02
