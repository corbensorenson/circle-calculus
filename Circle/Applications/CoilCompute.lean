/-!
Application seed for proof-carrying circular computation.

This module formalizes cyclic address wrapping for finite circular buffers.
Backend selection and performance claims are benchmark work, not proof claims.
-/

namespace Circle.Applications

def cyclicAddress (size index : Nat) : Nat :=
  index % size

theorem cyclicAddress_lt_size {size : Nat} (h : 0 < size) (index : Nat) :
    cyclicAddress size index < size := by
  unfold cyclicAddress
  exact Nat.mod_lt index h

theorem cyclicAddress_add_size {size : Nat} (h : 0 < size) (index : Nat) :
    cyclicAddress size (index + size) = cyclicAddress size index := by
  unfold cyclicAddress
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt index h)

end Circle.Applications
