/-!
Application seed for coil systems tracks.

This module formalizes a finite round-robin slot schedule for systems and
runtime examples. It does not prove fairness, load balancing, or performance.
-/

namespace Circle.Applications

def roundRobinSlot (slotCount tick : Nat) : Nat :=
  tick % slotCount

theorem roundRobinSlot_lt_slotCount {slotCount : Nat} (h : 0 < slotCount) (tick : Nat) :
    roundRobinSlot slotCount tick < slotCount := by
  unfold roundRobinSlot
  exact Nat.mod_lt tick h

theorem roundRobinSlot_add_slotCount {slotCount : Nat} (h : 0 < slotCount) (tick : Nat) :
    roundRobinSlot slotCount (tick + slotCount) = roundRobinSlot slotCount tick := by
  unfold roundRobinSlot
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt tick h)

theorem roundRobinSlot_add_mul_slotCount {slotCount : Nat} (_h : 0 < slotCount)
    (tick passes : Nat) :
    roundRobinSlot slotCount (tick + passes * slotCount) = roundRobinSlot slotCount tick := by
  unfold roundRobinSlot
  exact Nat.add_mul_mod_self_right tick passes slotCount

theorem roundRobinSlot_zero (slotCount : Nat) :
    roundRobinSlot slotCount 0 = 0 := by
  unfold roundRobinSlot
  simp

end Circle.Applications
