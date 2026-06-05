/-!
Application seed for CoilRay and CoilSampler.

This module formalizes a finite direction-bin schedule for rendering and
sampling queues. It does not prove any rendering performance claim.
-/

namespace Circle.Applications

def directionBin (binCount sample : Nat) : Nat :=
  sample % binCount

theorem directionBin_lt_binCount {binCount : Nat} (h : 0 < binCount) (sample : Nat) :
    directionBin binCount sample < binCount := by
  unfold directionBin
  exact Nat.mod_lt sample h

theorem directionBin_add_binCount {binCount : Nat} (h : 0 < binCount) (sample : Nat) :
    directionBin binCount (sample + binCount) = directionBin binCount sample := by
  unfold directionBin
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt sample h)

end Circle.Applications
