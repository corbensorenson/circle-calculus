import Circle.Core.Period
import Mathlib.Data.Nat.Prime.Basic

namespace Circle

/-- A full coil is a stride whose period is the whole circle size. -/
def fullCoil (n k : Nat) : Prop :=
  period n k = n

theorem fullCoil_iff_coprime {n k : Nat} (hn : n ≠ 0) :
    fullCoil n k ↔ Nat.Coprime n k := by
  unfold fullCoil
  rw [period_eq_n_div_gcd hn]
  constructor
  · intro h
    have hgcd : Nat.gcd n k = 1 := by
      rcases (Nat.div_eq_self.mp h) with hnzero | hgcd
      · exact False.elim (hn hnzero)
      · exact hgcd
    exact Nat.coprime_iff_gcd_eq_one.mpr hgcd
  · intro hcop
    rw [Nat.coprime_iff_gcd_eq_one.mp hcop, Nat.div_one]

theorem prime_full_coil {p k : Nat} (hp : Nat.Prime p) (hk0 : 0 < k) (hkp : k < p) :
    period p k = p := by
  have hp0 : p ≠ 0 := by exact hp.ne_zero
  rw [period_eq_n_div_gcd hp0]
  have hcop : Nat.Coprime p k := Nat.coprime_of_lt_prime hk0.ne' hkp hp
  have hgcd : Nat.gcd p k = 1 := Nat.coprime_iff_gcd_eq_one.mp hcop
  rw [hgcd, Nat.div_one]

end Circle
