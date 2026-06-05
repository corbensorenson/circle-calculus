import Circle.Core.Coil
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.ZMod.Units

namespace Circle

/-- Scaling multiplies a node by `k` in `C n`. -/
def scale (n k : Nat) (x : C n) : C n :=
  (k : ZMod n) * x

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

end Circle
