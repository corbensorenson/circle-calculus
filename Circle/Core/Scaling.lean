import Circle.Core.Period
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.ZMod.Units

namespace Circle

/-- Scaling multiplies a node by `k` in `C n`. -/
def scale (n k : Nat) (x : C n) : C n :=
  (k : ZMod n) * x

theorem scale_zero_factor (n : Nat) (x : C n) :
    scale n 0 x = 0 := by
  unfold scale
  simp

theorem scale_one (n : Nat) (x : C n) :
    scale n 1 x = x := by
  unfold scale
  simp

theorem scale_comp (n a b : Nat) (x : C n) :
    scale n a (scale n b x) = scale n (a * b) x := by
  unfold scale
  rw [← mul_assoc]
  norm_num

theorem scale_rot (n k stride : Nat) (x : C n) :
    scale n k (rot n stride x) = rot n (k * stride) (scale n k x) := by
  unfold scale rot
  rw [mul_add]
  norm_num

theorem scale_coilStep (n k stride start steps : Nat) :
    scale n k (coilStep n stride start steps) =
      coilStep n (k * stride) (k * start) steps := by
  unfold scale coilStep
  rw [mul_add]
  congr 1
  · norm_num
  · norm_num [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]

theorem scale_nat_to_coilStep (n k steps : Nat) :
    scale n k ((steps : Nat) : C n) = coilStep n k 0 steps := by
  unfold scale coilStep
  simp [Nat.mul_comm]

theorem scale_invertible_iff_coprime (n k : Nat) :
    Function.Bijective (scale n k) ↔ Nat.Coprime n k := by
  change Function.Bijective (fun x : ZMod n => (k : ZMod n) * x) ↔ Nat.Coprime n k
  rw [← IsUnit.isUnit_iff_mulLeft_bijective]
  rw [ZMod.isUnit_iff_coprime]
  exact ⟨Nat.Coprime.symm, Nat.Coprime.symm⟩

theorem prime_scale_bijective {p k : Nat} (hp : Nat.Prime p) (hk0 : 0 < k) (hkp : k < p) :
    Function.Bijective (scale p k) := by
  rw [scale_invertible_iff_coprime]
  exact Nat.coprime_of_lt_prime hk0.ne' hkp hp

theorem scale_cofactor_zero {n k : Nat} (hkn : k ∣ n) :
    scale n k ((n / k : Nat) : C n) = 0 := by
  unfold scale
  rw [← Nat.cast_mul]
  have hmul : k * (n / k) = n := Nat.mul_div_cancel' hkn
  rw [hmul]
  exact CharP.cast_eq_zero (ZMod n) n

theorem scale_cofactor_multiple_zero {n k m : Nat} (hkn : k ∣ n) :
    scale n k ((m * (n / k) : Nat) : C n) = 0 := by
  unfold scale
  rw [← Nat.cast_mul]
  have hmul : k * (n / k) = n := Nat.mul_div_cancel' hkn
  have hmul' : k * (m * (n / k)) = m * n := by
    rw [← Nat.mul_assoc]
    rw [Nat.mul_comm k m]
    rw [Nat.mul_assoc]
    rw [hmul]
  rw [hmul']
  rw [Nat.cast_mul]
  rw [CharP.cast_eq_zero (ZMod n) n]
  simp

theorem scale_add_cofactor_multiple {n k x m : Nat} (hkn : k ∣ n) :
    scale n k (((x + m * (n / k)) : Nat) : C n) = scale n k ((x : Nat) : C n) := by
  unfold scale
  rw [Nat.cast_add]
  rw [mul_add]
  have hzero := scale_cofactor_multiple_zero (n := n) (k := k) (m := m) hkn
  unfold scale at hzero
  rw [hzero]
  simp

theorem scale_nat_eq_zero_iff_dvd_mul (n k x : Nat) :
    scale n k ((x : Nat) : C n) = 0 ↔ n ∣ k * x := by
  unfold scale
  rw [← Nat.cast_mul]
  exact CharP.cast_eq_zero_iff (ZMod n) n (k * x)

theorem scale_nat_eq_zero_iff_period_dvd {n k x : Nat} (hn : n ≠ 0) :
    scale n k ((x : Nat) : C n) = 0 ↔ period n k ∣ x := by
  rw [period_eq_n_div_gcd hn]
  have hnpos : 0 < n := Nat.pos_of_ne_zero hn
  rw [scale_nat_eq_zero_iff_dvd_mul]
  let g := Nat.gcd n k
  have hgpos : 0 < g := Nat.gcd_pos_of_pos_left k hnpos
  have hgn : g ∣ n := Nat.gcd_dvd_left n k
  have hgk : g ∣ k := Nat.gcd_dvd_right n k
  have hn_decomp : n = g * (n / g) := by
    rw [Nat.mul_div_cancel' hgn]
  have hk_decomp : k = g * (k / g) := by
    rw [Nat.mul_div_cancel' hgk]
  have hcop : Nat.Coprime (n / g) (k / g) := Nat.coprime_div_gcd_div_gcd hgpos
  constructor
  · intro h
    have h1a : g * (n / g) ∣ k * x := by
      rw [← hn_decomp]
      exact h
    have h1b : g * (n / g) ∣ (g * (k / g)) * x := by
      rw [← hk_decomp]
      exact h1a
    have h1 : g * (n / g) ∣ g * ((k / g) * x) := by
      simpa [Nat.mul_assoc] using h1b
    have h2 : n / g ∣ (k / g) * x := (Nat.mul_dvd_mul_iff_left hgpos).mp h1
    exact hcop.dvd_of_dvd_mul_left h2
  · intro h
    have h2 : n / g ∣ (k / g) * x := dvd_mul_of_dvd_right h (k / g)
    have h1 : g * (n / g) ∣ g * ((k / g) * x) := (Nat.mul_dvd_mul_iff_left hgpos).mpr h2
    have h1b : g * (n / g) ∣ (g * (k / g)) * x := by
      simpa [Nat.mul_assoc] using h1
    have h1a : g * (n / g) ∣ k * x := by
      rw [hk_decomp]
      exact h1b
    rw [hn_decomp]
    exact h1a

theorem scale_nat_eq_iff_mul_modEq (n k x y : Nat) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔
      k * x ≡ k * y [MOD n] := by
  unfold scale
  rw [← Nat.cast_mul, ← Nat.cast_mul]
  exact ZMod.natCast_eq_natCast_iff (k * x) (k * y) n

theorem scale_nat_eq_iff_nat_modEq_of_coprime {n k x y : Nat} (hcop : Nat.Coprime n k) :
    scale n k ((x : Nat) : C n) = scale n k ((y : Nat) : C n) ↔ x ≡ y [MOD n] := by
  have hbij : Function.Bijective (scale n k) := (scale_invertible_iff_coprime n k).mpr hcop
  constructor
  · intro h
    have hxy : ((x : Nat) : C n) = ((y : Nat) : C n) := hbij.1 h
    exact (ZMod.natCast_eq_natCast_iff x y n).mp hxy
  · intro h
    have hxy : ((x : Nat) : C n) = ((y : Nat) : C n) :=
      (ZMod.natCast_eq_natCast_iff x y n).mpr h
    exact congrArg (scale n k) hxy

theorem scale_factor_modEq {n k l : Nat} (h : k ≡ l [MOD n]) (x : C n) :
    scale n k x = scale n l x := by
  unfold scale
  have hcast : ((k : Nat) : ZMod n) = ((l : Nat) : ZMod n) :=
    (ZMod.natCast_eq_natCast_iff k l n).mpr h
  rw [hcast]

end Circle
