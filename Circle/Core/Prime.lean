import Circle.Core.Period
import Mathlib.Data.Nat.Prime.Basic

namespace Circle

/-- A full coil is a stride whose period is the whole circle size. -/
def fullCoil (n k : Nat) : Prop :=
  period n k = n

theorem prime_full_coil {p k : Nat} (hp : Nat.Prime p) (hk0 : 0 < k) (hkp : k < p) :
    period p k = p := by
  have hp0 : p ≠ 0 := by exact hp.ne_zero
  rw [period_eq_n_div_gcd hp0]
  have hcop : Nat.Coprime p k := Nat.coprime_of_lt_prime hk0.ne' hkp hp
  have hgcd : Nat.gcd p k = 1 := Nat.coprime_iff_gcd_eq_one.mp hcop
  rw [hgcd, Nat.div_one]

end Circle
