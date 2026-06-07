/-!
Application seeds for Circle AI tracks.

These definitions formalize finite schedule/indexing primitives for AI
experiments. They do not prove model quality, efficiency, or general AI
improvement.
-/

namespace Circle.Applications

def phaseChannel (period position : Nat) : Nat :=
  position % period

theorem phaseChannel_lt_period {period : Nat} (h : 0 < period) (position : Nat) :
    phaseChannel period position < period := by
  unfold phaseChannel
  exact Nat.mod_lt position h

theorem phaseChannel_add_period {period : Nat} (h : 0 < period) (position : Nat) :
    phaseChannel period (position + period) = phaseChannel period position := by
  unfold phaseChannel
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt position h)

theorem phaseChannel_add_mul_period {period : Nat} (_h : 0 < period)
    (position passes : Nat) :
    phaseChannel period (position + passes * period) = phaseChannel period position := by
  unfold phaseChannel
  exact Nat.add_mul_mod_self_right position passes period

theorem phaseChannel_idempotent (period position : Nat) :
    phaseChannel period (phaseChannel period position) = phaseChannel period position := by
  unfold phaseChannel
  by_cases h : period = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt position (Nat.pos_of_ne_zero h))

theorem phaseChannel_zero (period : Nat) :
    phaseChannel period 0 = 0 := by
  unfold phaseChannel
  simp

def memorySlot (bankSize token : Nat) : Nat :=
  token % bankSize

theorem memorySlot_lt_bankSize {bankSize : Nat} (h : 0 < bankSize) (token : Nat) :
    memorySlot bankSize token < bankSize := by
  unfold memorySlot
  exact Nat.mod_lt token h

theorem memorySlot_add_bankSize {bankSize : Nat} (h : 0 < bankSize) (token : Nat) :
    memorySlot bankSize (token + bankSize) = memorySlot bankSize token := by
  unfold memorySlot
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt token h)

theorem memorySlot_add_mul_bankSize {bankSize : Nat} (_h : 0 < bankSize)
    (token passes : Nat) :
    memorySlot bankSize (token + passes * bankSize) = memorySlot bankSize token := by
  unfold memorySlot
  exact Nat.add_mul_mod_self_right token passes bankSize

theorem memorySlot_idempotent (bankSize token : Nat) :
    memorySlot bankSize (memorySlot bankSize token) = memorySlot bankSize token := by
  unfold memorySlot
  by_cases h : bankSize = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt token (Nat.pos_of_ne_zero h))

theorem memorySlot_zero (bankSize : Nat) :
    memorySlot bankSize 0 = 0 := by
  unfold memorySlot
  simp

def loopRequiredSteps (loopPeriod sample : Nat) : Nat :=
  phaseChannel loopPeriod sample + 1

theorem loopRequiredSteps_pos (loopPeriod sample : Nat) :
    0 < loopRequiredSteps loopPeriod sample := by
  unfold loopRequiredSteps
  exact Nat.succ_pos _

theorem loopRequiredSteps_le_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample : Nat) :
    loopRequiredSteps loopPeriod sample ≤ loopPeriod := by
  unfold loopRequiredSteps phaseChannel
  exact Nat.succ_le_of_lt (Nat.mod_lt sample h)

theorem loopRequiredSteps_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample : Nat) :
    loopRequiredSteps loopPeriod (sample + loopPeriod) =
      loopRequiredSteps loopPeriod sample := by
  unfold loopRequiredSteps
  rw [phaseChannel_add_period h]

def tokenRecurrenceBudget (loopPeriod token : Nat) : Nat :=
  loopRequiredSteps loopPeriod token

theorem tokenRecurrenceBudget_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (token : Nat) :
    tokenRecurrenceBudget loopPeriod (token + loopPeriod) =
      tokenRecurrenceBudget loopPeriod token := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_add_loopPeriod h token

theorem tokenRecurrenceBudget_le_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (token : Nat) :
    tokenRecurrenceBudget loopPeriod token ≤ loopPeriod := by
  unfold tokenRecurrenceBudget
  exact loopRequiredSteps_le_loopPeriod h token

def trainingFreeLoopBudget (loopPeriod sample maxLoops : Nat) : Nat :=
  min (loopRequiredSteps loopPeriod sample) maxLoops

theorem trainingFreeLoopBudget_le_maxLoops (loopPeriod sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod sample maxLoops ≤ maxLoops := by
  unfold trainingFreeLoopBudget
  exact Nat.min_le_right _ _

theorem trainingFreeLoopBudget_le_requiredSteps (loopPeriod sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod sample maxLoops ≤
      loopRequiredSteps loopPeriod sample := by
  unfold trainingFreeLoopBudget
  exact Nat.min_le_left _ _

theorem trainingFreeLoopBudget_add_loopPeriod {loopPeriod : Nat} (h : 0 < loopPeriod)
    (sample maxLoops : Nat) :
    trainingFreeLoopBudget loopPeriod (sample + loopPeriod) maxLoops =
      trainingFreeLoopBudget loopPeriod sample maxLoops := by
  unfold trainingFreeLoopBudget
  rw [loopRequiredSteps_add_loopPeriod h]

def loopExitAvailable (loopPeriod sample maxLoops : Nat) : Prop :=
  loopRequiredSteps loopPeriod sample ≤ maxLoops

theorem trainingFreeLoopBudget_eq_required_of_available
    (loopPeriod sample maxLoops : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops) :
    trainingFreeLoopBudget loopPeriod sample maxLoops =
      loopRequiredSteps loopPeriod sample := by
  unfold trainingFreeLoopBudget loopExitAvailable at *
  exact Nat.min_eq_left hbudget

def loopOverthinkingBoundary (loopPeriod sample tolerance : Nat) : Nat :=
  loopRequiredSteps loopPeriod sample + tolerance

structure LoopExitCertificate where
  loopPeriod : Nat
  sample : Nat
  maxLoops : Nat
  tolerance : Nat
  exitStep : Nat
  exactRequired : exitStep = loopRequiredSteps loopPeriod sample
  withinBudget : exitStep ≤ maxLoops
  withinGuardrail : exitStep ≤ loopOverthinkingBoundary loopPeriod sample tolerance

def loopExitCertificate
    (loopPeriod sample maxLoops tolerance : Nat)
    (hbudget : loopExitAvailable loopPeriod sample maxLoops) :
    LoopExitCertificate :=
  { loopPeriod := loopPeriod,
    sample := sample,
    maxLoops := maxLoops,
    tolerance := tolerance,
    exitStep := loopRequiredSteps loopPeriod sample,
    exactRequired := rfl,
    withinBudget := hbudget,
    withinGuardrail := by
      unfold loopOverthinkingBoundary
      exact Nat.le_add_right _ _ }

theorem loopOverthinkingBoundary_ge_required
    (loopPeriod sample tolerance : Nat) :
    loopRequiredSteps loopPeriod sample ≤
      loopOverthinkingBoundary loopPeriod sample tolerance := by
  unfold loopOverthinkingBoundary
  exact Nat.le_add_right _ _

theorem loopOverthinkingBoundary_add_loopPeriod
    {loopPeriod : Nat} (hpositive : 0 < loopPeriod)
    (sample tolerance : Nat) :
    loopOverthinkingBoundary loopPeriod (sample + loopPeriod) tolerance =
      loopOverthinkingBoundary loopPeriod sample tolerance := by
  unfold loopOverthinkingBoundary
  rw [loopRequiredSteps_add_loopPeriod hpositive]

theorem loopExitAvailable_of_loopPeriod_le_budget
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (hbudget : loopPeriod ≤ maxLoops) (sample : Nat) :
    loopExitAvailable loopPeriod sample maxLoops := by
  unfold loopExitAvailable
  exact Nat.le_trans (loopRequiredSteps_le_loopPeriod hpositive sample) hbudget

theorem loopExitAvailable_add_loopPeriod
    {loopPeriod maxLoops : Nat} (hpositive : 0 < loopPeriod)
    (sample : Nat) :
    loopExitAvailable loopPeriod (sample + loopPeriod) maxLoops ↔
      loopExitAvailable loopPeriod sample maxLoops := by
  unfold loopExitAvailable
  rw [loopRequiredSteps_add_loopPeriod hpositive]

theorem loopExitCertificate_exit_eq_required
    (certificate : LoopExitCertificate) :
    certificate.exitStep =
      loopRequiredSteps certificate.loopPeriod certificate.sample :=
  certificate.exactRequired

theorem loopExitCertificate_within_budget
    (certificate : LoopExitCertificate) :
    certificate.exitStep ≤ certificate.maxLoops :=
  certificate.withinBudget

theorem loopExitCertificate_within_guardrail
    (certificate : LoopExitCertificate) :
    certificate.exitStep ≤
      loopOverthinkingBoundary
        certificate.loopPeriod certificate.sample certificate.tolerance :=
  certificate.withinGuardrail

def adapterBlock (blockSize channel : Nat) : Nat :=
  channel % blockSize

theorem adapterBlock_lt_blockSize {blockSize : Nat} (h : 0 < blockSize) (channel : Nat) :
    adapterBlock blockSize channel < blockSize := by
  unfold adapterBlock
  exact Nat.mod_lt channel h

theorem adapterBlock_add_blockSize {blockSize : Nat} (h : 0 < blockSize) (channel : Nat) :
    adapterBlock blockSize (channel + blockSize) = adapterBlock blockSize channel := by
  unfold adapterBlock
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt channel h)

theorem adapterBlock_add_mul_blockSize {blockSize : Nat} (_h : 0 < blockSize)
    (channel passes : Nat) :
    adapterBlock blockSize (channel + passes * blockSize) = adapterBlock blockSize channel := by
  unfold adapterBlock
  exact Nat.add_mul_mod_self_right channel passes blockSize

theorem adapterBlock_idempotent (blockSize channel : Nat) :
    adapterBlock blockSize (adapterBlock blockSize channel) = adapterBlock blockSize channel := by
  unfold adapterBlock
  by_cases h : blockSize = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt channel (Nat.pos_of_ne_zero h))

theorem adapterBlock_zero (blockSize : Nat) :
    adapterBlock blockSize 0 = 0 := by
  unfold adapterBlock
  simp

end Circle.Applications
