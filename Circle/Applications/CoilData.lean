/-!
Application seed for coil data analysis.

This module formalizes only a finite phase coordinate for synthetic periodic
data. Benchmarks and real-data claims remain outside this theorem seed.
-/

namespace Circle.Applications

def phaseCoordinate (period step : Nat) : Nat :=
  step % period

theorem phaseCoordinate_lt_period {period : Nat} (h : 0 < period) (step : Nat) :
    phaseCoordinate period step < period := by
  unfold phaseCoordinate
  exact Nat.mod_lt step h

theorem phaseCoordinate_add_period {period : Nat} (h : 0 < period) (step : Nat) :
    phaseCoordinate period (step + period) = phaseCoordinate period step := by
  unfold phaseCoordinate
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero]
  exact Nat.mod_eq_of_lt (Nat.mod_lt step h)

theorem phaseCoordinate_add_mul_period {period : Nat} (_h : 0 < period)
    (step passes : Nat) :
    phaseCoordinate period (step + passes * period) = phaseCoordinate period step := by
  unfold phaseCoordinate
  exact Nat.add_mul_mod_self_right step passes period

theorem phaseCoordinate_idempotent (period step : Nat) :
    phaseCoordinate period (phaseCoordinate period step) = phaseCoordinate period step := by
  unfold phaseCoordinate
  by_cases h : period = 0
  · simp [h]
  · exact Nat.mod_eq_of_lt (Nat.mod_lt step (Nat.pos_of_ne_zero h))

theorem phaseCoordinate_zero (period : Nat) :
    phaseCoordinate period 0 = 0 := by
  unfold phaseCoordinate
  simp

end Circle.Applications
