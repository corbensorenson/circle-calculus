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
